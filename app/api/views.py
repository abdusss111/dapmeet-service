from rest_framework import generics, status from rest_framework.response import Response from rest_framework.permissions import IsAuthenticated from rest_framework.views import APIView from 
django.shortcuts import get_object_or_404 from .models import Meeting from .serializers import (
    MeetingCreateSerializer, MeetingPatchSerializer, MeetingSerializer, MessageSerializer, ) class MeetingListCreateView(generics.ListCreateAPIView): permission_classes = [IsAuthenticated] 
    serializer_class = MeetingSerializer def get_queryset(self):
        return Meeting.objects.filter(user=self.request.user)
    def post(self, request, *args, **kwargs):
        serializer = MeetingCreateSerializer(data=request.data) serializer.is_valid(raise_exception=True) meeting = serializer.save(user=request.user) return 
        Response(MeetingSerializer(meeting).data, status=status.HTTP_201_CREATED)
class MeetingDetailView(APIView):
    permission_classes = [IsAuthenticated] def get_object(self, meeting_id):
        return get_object_or_404(Meeting, id=meeting_id, user=self.request.user)
    def get(self, request, meeting_id):
        meeting = self.get_object(meeting_id) return Response(MeetingSerializer(meeting).data)
    def patch(self, request, meeting_id):
        meeting = self.get_object(meeting_id) serializer = MeetingPatchSerializer(meeting, data=request.data, partial=True) serializer.is_valid(raise_exception=True) serializer.save() return 
        Response(MeetingSerializer(meeting).data)
class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated] def get(self, request):
        meeting_id = request.query_params.get("meeting_id") meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user) return Response(meeting.chat_history or [])
    def post(self, request):
        meeting_id = request.data.get("meeting_id") messages = request.data.get("history") meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user) # Validate messages serializer = 
        MessageSerializer(data=messages, many=True) serializer.is_valid(raise_exception=True) meeting.chat_history = serializer.data meeting.save() return Response({"status": "ok"})
