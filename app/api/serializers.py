from rest_framework import serializers from .models import Meeting class MessageSerializer(serializers.Serializer):
    id = serializers.CharField() role = serializers.ChoiceField(choices=["user", "assistant"]) content = serializers.CharField() class MeetingCreateSerializer(serializers.ModelSerializer): class 
    Meta:
        model = Meeting fields = ["title"] class MeetingPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting fields = ["title", "transcript"] class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting fields = "__all__"
