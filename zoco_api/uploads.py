from rest_framework import serializers

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


class ImageUploadSerializer(serializers.Serializer):
    """Valida una imagen subida: debe ser una imagen real (Pillow) de máximo 5 MB."""

    image = serializers.ImageField()

    def validate_image(self, value):
        if value.size > MAX_IMAGE_BYTES:
            raise serializers.ValidationError("La imagen no puede pesar más de 5 MB.")
        return value
