"""
Кастомные поле для работы с изображением в base64.
"""

from drf_extra_fields.fields import Base64ImageField as DRFBase64ImageField

#: Позволяет передавать изображения как строки в JSON запросах
Base64ImageField = DRFBase64ImageField 