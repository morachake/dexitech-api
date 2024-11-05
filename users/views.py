from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer