from rest_framework import serializers

class OCRSerializers(serializers.Serializer):
    cv = serializers.FileField()

    def validate_cv(self, file):
        if not file.name.endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            raise serializers.ValidationError("File harus berupa gambar atau PDF")
        return file