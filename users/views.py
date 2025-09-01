import base64
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import FaceCompareResponseSerializer, UserPasswordChangeSerializer, \
    UserRegistrationSerializer, UserLoginSerializer, UploadPassportSerializer, UploadFaceSerializer
from .models import FaceComparison, AbstractUser


from rest_framework_simplejwt.tokens import RefreshToken
from .models import GlobalUserContact
from .serializers import GlobalContactSerializer
from .serializers import UserContactSerializer
# faceid/views.py
import os
import cv2
import base64
import tempfile
import traceback
import numpy as np
from PIL import Image, ExifTags
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from deepface import DeepFace

# ===== LOYIHAGA MOS QILING =====
# from .serializers import UploadPassportSerializer, UploadFaceSerializer, FaceCompareResponseSerializer
# from .models import FaceComparison

DEBUG_FACEID = True  # production uchun False qiling
# Agar settings.py da belgilagan bo'lsangiz, o'shani oladi; aks holda default 0.50
FACE_MATCH_THRESHOLD = getattr(settings, "FACE_MATCH_THRESHOLD", 0.50)


def correct_image_orientation(image_path):
    """
    EXIF orientatsiyasini to'g'rilab, OpenCV (BGR) ndarray qaytaradi.
    """
    try:
        image = Image.open(image_path)
        orientation_key = None
        for k, v in ExifTags.TAGS.items():
            if v == "Orientation":
                orientation_key = k
                break

        if orientation_key is not None:
            exif = image._getexif()
            if exif is not None:
                val = exif.get(orientation_key, 1)
                if val == 3:
                    image = image.rotate(180, expand=True)
                elif val == 6:
                    image = image.rotate(270, expand=True)
                elif val == 8:
                    image = image.rotate(90, expand=True)

        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print("EXIF correction error:", e)
        return cv2.imread(image_path)


def respond_error(msg, status=400, exc=None):
    """
    DEBUG_FACEID True bo'lsa, exceptionni ham qaytaradi.
    """
    if DEBUG_FACEID and exc is not None:
        print("TRACEBACK:", traceback.format_exc())
        return Response({"error": f"{msg}: {str(exc)}"}, status=status)
    return Response({"error": msg}, status=status)


class UploadPassportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # serializerni loyihaga mos import qiling
        serializer = UploadPassportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        passport_file = serializer.validated_data['passport_image']
        image_bytes = passport_file.read()

        # passport rasmni cache ga base64 qilib saqlaymiz (key user-specific)
        try:
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            cache.set(f"passport_image_{request.user.id}", encoded_image, timeout=300)
        except Exception as e:
            return respond_error("Rasmni kodlashda xato", 400, e)

        passport_path = None
        temp_img_path = None
        temp_face_crop_path = None

        try:
            # 1) vaqtinchalik passportni diskga yozish
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(image_bytes)
                f.flush()
                passport_path = f.name

            # 2) EXIF correction
            img = correct_image_orientation(passport_path)
            if img is None or img.size == 0:
                return respond_error("Rasm o'qib bo'lmadi", 400)

            # 3) agar juda kichik bo'lsa kattalashtirish
            h, w = img.shape[:2]
            if h < 300 or w < 300:
                img = cv2.resize(img, (max(300, w * 2), max(300, h * 2)), interpolation=cv2.INTER_CUBIC)

            # 4) DeepFace.extract_faces uchun vaqtincha .jpg ga yozamiz
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                cv2.imwrite(tmp.name, img)  # img BGR
                temp_img_path = tmp.name

            # 5) yuzni aniqlash (bir necha backend sinov)
            face_img_rgb = None
            for backend in ["retinaface", "mtcnn", "opencv"]:
                try:
                    faces = DeepFace.extract_faces(
                        img_path=temp_img_path,
                        detector_backend=backend,
                        enforce_detection=False
                    )
                    if faces and isinstance(faces, list):
                        first = faces[0]
                        # defensive: DeepFace qaytishi har xil bo'lishi mumkin
                        if isinstance(first, dict) and "face" in first:
                            face = first["face"]
                        else:
                            face = first
                        if isinstance(face, np.ndarray) and min(face.shape[:2]) >= 32:
                            face_img_rgb = face  # RGB ndarray
                            print(f"{backend} yuzni topdi: {face.shape}")
                            break
                except Exception as be:
                    print(f"{backend} backend error:", be)

            if face_img_rgb is None:
                return respond_error("Yuz aniqlanmadi, boshqa rasm yuklang", 400)

            # 6) float64 -> uint8 (DeepFace ko'pincha 0..1 float64 qaytaradi)
            face_uint8 = face_img_rgb
            if not isinstance(face_uint8, np.ndarray):
                return respond_error("Yuz ma'lumot formati noto'g'ri", 400)
            if face_uint8.dtype != np.uint8:
                face_uint8 = (face_uint8 * 255).clip(0, 255).astype(np.uint8)

            # 7) cropni vaqtincha saqlash va embedding olish
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_face:
                cv2.imwrite(tmp_face.name, cv2.cvtColor(face_uint8, cv2.COLOR_RGB2BGR))
                temp_face_crop_path = tmp_face.name

            embedding_dict = DeepFace.represent(
                img_path=temp_face_crop_path,
                model_name="ArcFace",
                detector_backend="skip",
                enforce_detection=False
            )
            passport_vec = np.array(embedding_dict[0]["embedding"], dtype=np.float32)
            cache.set(f"passport_embedding_{request.user.id}", passport_vec, timeout=300)

        except Exception as e:
            return respond_error("Xato yuz berdi", 400, e)

        finally:
            for p in [passport_path, temp_img_path, temp_face_crop_path]:
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception as ex:
                        print("Faylni o'chirish xato:", ex)

        return Response({"message": "Passport rasmi saqlandi ✅"}, status=200)


class CompareFaceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadFaceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        face_file = serializer.validated_data["face_image"]
        face_bytes = face_file.read()

        # avvalgi saqlangan passport embedding va image
        passport_vec = cache.get(f"passport_embedding_{request.user.id}")
        passport_image_encoded = cache.get(f"passport_image_{request.user.id}")

        if passport_vec is None or passport_image_encoded is None:
            return respond_error("Passport rasmi topilmadi yoki vaqti o'tib ketgan", 400)

        face_path = None
        temp_img_path = None
        temp_face_crop_path = None

        try:
            # 1) vaqtinchalik selfie diskga yozish
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(face_bytes)
                f.flush()
                face_path = f.name

            # 2) EXIF correction
            img = correct_image_orientation(face_path)
            if img is None or img.size == 0:
                return Response({"match_result": False, "message": "Rasm o'qib bo'lmadi"}, status=200)

            # 3) kichik bo'lsa kattalashtirish
            h, w = img.shape[:2]
            if h < 300 or w < 300:
                img = cv2.resize(img, (max(300, w * 2), max(300, h * 2)), interpolation=cv2.INTER_CUBIC)

            # 4) DeepFace.extract_faces uchun vaqtincha .jpg
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                cv2.imwrite(tmp.name, img)
                temp_img_path = tmp.name

            # 5) yuz aniqlash
            face_img_rgb = None
            for backend in ["retinaface", "mtcnn", "opencv"]:
                try:
                    faces = DeepFace.extract_faces(
                        img_path=temp_img_path,
                        detector_backend=backend,
                        enforce_detection=False
                    )
                    if faces and isinstance(faces, list):
                        first = faces[0]
                        if isinstance(first, dict) and "face" in first:
                            face = first["face"]
                        else:
                            face = first
                        if isinstance(face, np.ndarray) and min(face.shape[:2]) >= 32:
                            face_img_rgb = face
                            print(f"{backend} yuzni topdi: {face.shape}")
                            break
                except Exception as be:
                    print(f"{backend} backend error:", be)

            if face_img_rgb is None:
                return Response({"match_result": False, "message": "Yuz aniqlanmadi, boshqa rasm yuklang"}, status=200)

            # 6) float64 -> uint8 agar kerak bo'lsa
            face_uint8 = face_img_rgb
            if not isinstance(face_uint8, np.ndarray):
                return Response({"match_result": False, "message": "Yuz ma'lumot formati noto'g'ri"}, status=200)
            if face_uint8.dtype != np.uint8:
                face_uint8 = (face_uint8 * 255).clip(0, 255).astype(np.uint8)

            # 7) represent uchun cropni .jpg ga yozish
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_face:
                cv2.imwrite(tmp_face.name, cv2.cvtColor(face_uint8, cv2.COLOR_RGB2BGR))
                temp_face_crop_path = tmp_face.name

            embedding_dict = DeepFace.represent(
                img_path=temp_face_crop_path,
                model_name="ArcFace",
                detector_backend="skip",
                enforce_detection=False
            )
            face_vec = np.array(embedding_dict[0]["embedding"], dtype=np.float32)

            # 8) Similarity (cosine)
            assport_vec = passport_vec / np.linalg.norm(passport_vec)
            face_vec = face_vec / np.linalg.norm(face_vec)

            similarity = float(np.dot(passport_vec, face_vec))
            print(f"Similarity: {similarity:.6f}")

            # 9) Threshold (settings orqali sozlanishi mumkin)
            threshold = FACE_MATCH_THRESHOLD  # default 0.50, lekin 0.35 qilish tavsiya
            match = similarity >= threshold

            if not match:
                # agar mos bo'lmasa passport cache'ini tozalash — qayta yuklash talab qilinadi
                cache.delete(f"passport_embedding_{request.user.id}")
                cache.delete(f"passport_image_{request.user.id}")
                return Response({
                    "match_result": False,
                    "message": "Bu boshqa odam bo'lishi mumkin.",
                    "similarity": similarity,
                    "threshold": threshold
                }, status=200)

            # 10) Mos keldi — DB ga saqlash (model import qiling)
            passport_content = ContentFile(base64.b64decode(passport_image_encoded), "passport.jpg")
            face_content = ContentFile(face_bytes, "face.jpg")

            comparison = FaceComparison.objects.create(
                user=request.user,
                passport_image=passport_content,
                face_image=face_content,
                match_result=True
            )

            response_serializer = FaceCompareResponseSerializer(comparison, context={"request": request})
            data = response_serializer.data
            data.update({"similarity": similarity, "threshold": threshold})
            return Response(data, status=200)

        except Exception as e:
            print("Self yuzda xato:", traceback.format_exc())
            msg = f"Yuzni tekshirishda xato: {str(e)}" if DEBUG_FACEID else "Yuzni tekshirishda xato"
            return Response({"match_result": False, "message": msg}, status=200)

        finally:
            for p in [face_path, temp_img_path, temp_face_crop_path]:
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception as ex:
                        print("Fayl o'chirishda xato:", ex)


class UserRegistrationView(generics.CreateAPIView):
    queryset = AbstractUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": self.get_serializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role  # Bu qatorni qoldirsang JWT token ichida "role" field ham bo‘ladi

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserRegistrationSerializer(user).data,
        }, status=status.HTTP_200_OK)


class UserPasswordChangeView(generics.GenericAPIView):
    serializer_class = UserPasswordChangeSerializer
    permission_classes = [IsAuthenticated]  # faqat user roli bo‘lsa

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully."})


class UpdateContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserContactSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Kontakt ma'lumotlari yangilandi.", "data": serializer.data})
        return Response(serializer.errors, status=400)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserContactSerializer(
            user,
            data=request.data,
            partial=True,  # bu yerda `partial=True` bo‘lishi orqali PATCH kabi harakat qiladi
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profil muvaffaqiyatli yangilandi.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # faqat token bo‘lsa yetarli

    def get(self, request):
        try:
            # JWT token orqali kelgan user.id ni modelda tekshirish
            user = AbstractUser.objects.get(id=request.user.id)
        except AbstractUser.DoesNotExist:
            return Response({
                "message": "Foydalanuvchi ro‘yxatdan o‘tmagan yoki o‘chirilgan."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UserContactSerializer(user, context={"request": request})
        return Response({
            "message": "Foydalanuvchi ma'lumotlari muvaffaqiyatli olindi.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout muvaffaqiyatli bajarildi."})
        except Exception as e:
            return Response({"Logout hato bajarildi": str(e)}, status=400)


class ProfileImageDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        delete_flag = str(request.query_params.get("delete", "")).lower()

        if delete_flag not in ["true", "1"]:
            return Response({"message": "`delete=true` query parametri yuborilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if user.image:
            user.image.delete(save=False)
            user.image = None
            user.save()
            return Response({"message": "Profil rasmi o‘chirildi."}, status=status.HTTP_200_OK)

        return Response({"message": "Profil rasmi mavjud emas edi."}, status=status.HTTP_400_BAD_REQUEST)


class GlobalContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contact = GlobalUserContact.objects.first()
        if not contact:
            return Response({"detail": "Ma'lumotlar mavjud emas."}, status=404)
        serializer = GlobalContactSerializer(contact)
        return Response(serializer.data)


class ViewPassportImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        encoded_passport = cache.get(f"passport_{request.user.id}")
        if not encoded_passport:
            return Response({"error": "Passport rasmi topilmadi"}, status=404)

        passport_bytes = base64.b64decode(encoded_passport)
        return HttpResponse(passport_bytes, content_type="image/jpeg")


class ViewFaceImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        encoded_face = cache.get(f"face_{request.user.id}")
        if not encoded_face:
            return Response({"error": "Yuz rasmi topilmadi"}, status=404)

        face_bytes = base64.b64decode(encoded_face)
        return HttpResponse(face_bytes, content_type="image/jpeg")
