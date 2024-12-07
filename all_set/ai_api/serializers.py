from rest_framework import serializers

class GenerateQuestionsSerializer(serializers.Serializer):
    resume = serializers.FileField(required=True)
    job_title = serializers.CharField(max_length=255)
    job_description = serializers.CharField(allow_blank=True, required=False)


class GetResultsSerializer(serializers.Serializer):
    question = serializers.CharField(
        max_length=500,  # Adjust the max length as needed
        required=True
    )
    answer = serializers.CharField(
        max_length=2000,  # Adjust the max length as needed
        required=False
    )