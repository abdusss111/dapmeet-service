from django.urls import path
from .views import MeetingListCreateView, MeetingDetailView, ChatHistoryView
urlpatterns = [
    path("api/meetings/", MeetingListCreateView.as_view()), path("api/meetings/<uuid:meeting_id>/", MeetingDetailView.as_view()), path("api/chat/history/", ChatHistoryView.as_view()), ]
