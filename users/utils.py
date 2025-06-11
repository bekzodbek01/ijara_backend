# # Masalan, users/validators.py fayliga joylashtir
# from PIL import Image
# from rest_framework.exceptions import ValidationError
#
# ALLOWED_FORMATS = ['JPEG', 'JPG', 'PNG', 'HEIC', 'HEIF']
#
# def validate_image_format(image_file):
#     try:
#         img = Image.open(image_file)
#         if img.format.upper() not in ALLOWED_FORMATS:
#             raise ValidationError(f"Ruxsat etilmagan format: {img.format}. Faqat {', '.join(ALLOWED_FORMATS)} formatlarga ruxsat beriladi.")
#         image_file.seek(0)  # File pointerni reset qilamiz
#     except Exception:
#         raise ValidationError("Yaroqsiz yoki buzilgan rasm fayli!")
