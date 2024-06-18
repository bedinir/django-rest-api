from rest_framework import generics, viewsets,status
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from api import models
from api import permissions
from api import serializer

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializer import RegisterSerializer, LoginSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = serializer.validated_data['token']
        return Response({
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'token': token.key
        }, status=status.HTTP_200_OK)

class UserProfileFeedViewSet(viewsets.ModelViewSet):
    """Handles creating, reading and updating profile feed items"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializer.ProfileFeedItemSerializer
    queryset = models.ProfileFeedItem.objects.all()

    permission_classes = (
        permissions.UpdateOwnStatus,
        IsAuthenticatedOrReadOnly
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged in user"""
        serializer.save(user_profile=self.request.user)

class StateViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializer.StateSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class CityViewSet(viewsets.ModelViewSet):
    queryset = models.City.objects.all()
    serializer_class = serializer.CitySerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class BrandViewSet(viewsets.ModelViewSet):
    queryset = models.Brand.objects.all()
    serializer_class = serializer.BrandSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializer.CategorySerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]
class ProductActivateDeactivateView(generics.UpdateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductActivationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & permissions.IsAdmin]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        is_active = serializer.validated_data['is_active']
        instance.is_active = is_active
        instance.save()
        
        return Response(serializer.ProductSerializer(instance).data)


class CartViewSet(viewsets.ModelViewSet):
    queryset = models.Cart.objects.all()
    serializer_class = serializer.CartSerializer
    authentication_classes = [TokenAuthentication]

    permission_classes = [IsAuthenticated, permissions.IsOwner, permissions.IsCustomer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializer.OrderSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return models.Order.objects.all()
        return models.Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'pending':
            return Response({"detail": "Cannot update order unless it is in 'pending' status."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'pending':
            return Response({"detail": "Cannot delete order unless it is in 'pending' status."},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)