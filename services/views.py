from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError
from .models import Service
from .serializers import ServiceSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        try:
            # Validate required fields
            if not request.data.get('name'):
                raise ValidationError('Service name is required')
            if not request.data.get('description'):
                raise ValidationError('Service description is required')
                
            # Check if service name already exists
            if Service.objects.filter(name__iexact=request.data.get('name')).exists():
                raise ValidationError('A service with this name already exists')
            
            # Validate icon if provided
            icon = request.FILES.get('icon')
            if icon:
                if not icon.content_type.startswith('image/'):
                    raise ValidationError('Icon must be an image file')
                if icon.size > 5 * 1024 * 1024:  # 5MB limit
                    raise ValidationError('Icon size should not exceed 5MB')
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response({
                'status': 'success',
                'message': 'Service created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating the service'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)