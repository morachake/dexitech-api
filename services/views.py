from rest_framework import viewsets
from .models import ServiceCategory, Service
from .serializers import ServiceCategorySerializer, ServiceSerializer

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        queryset = Service.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)
        return queryset