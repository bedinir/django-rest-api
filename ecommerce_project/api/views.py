from rest_framework import generics, viewsets,status,views
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from .authentication import CustomTokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db import transaction
from .serializer import ProductActivationSerializer, ProductSerializer, OrderSerializer

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
            'token': token
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
    authentication_classes = [CustomTokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class CityViewSet(viewsets.ModelViewSet):
    queryset = models.City.objects.all()
    serializer_class = serializer.CitySerializer
    authentication_classes = [CustomTokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class BrandViewSet(viewsets.ModelViewSet):
    queryset = models.Brand.objects.all()
    serializer_class = serializer.BrandSerializer
    authentication_classes = [CustomTokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializer.CategorySerializer
    authentication_classes = [CustomTokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductSerializer
    authentication_classes = [CustomTokenAuthentication]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated & permissions.IsAdmin]
        else:
            permission_classes = [IsAuthenticated & (permissions.IsAdmin | permissions.IsCustomer)]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            return models.Product.objects.all()
        elif user.is_authenticated and user.role == 'customer':
            return models.Product.objects.filter(is_active=True, stock_quantity__gt=0)
        return models.Product.objects.none()
class ProductActivateDeactivateView(generics.UpdateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductActivationSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated & permissions.IsAdmin]

    def patch(self, request, pk):
        try:
            product = models.Product.objects.get(pk=pk)
        except models.Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductActivationSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartViewSet(viewsets.ModelViewSet):
    queryset = models.Cart.objects.all()
    serializer_class = serializer.CartSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated, permissions.IsOwner, permissions.IsCustomer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomTokenAuthentication]
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
        if instance.status != 'PENDING':
            return Response({"detail": "Cannot update order unless it is in 'PENDING' status."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'PENDING':
            return Response({"detail": "Cannot delete order unless it is in 'PENDING' status."},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CartToOrderView(views.APIView):
    permission_classes = [IsAuthenticated, permissions.IsCustomer]
    authentication_classes = [CustomTokenAuthentication]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = models.Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"detail": "No items in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        created_orders = []
        for cart_item in cart_items:
            product = cart_item.product
            order_data = {
                "product": product.id,
                "quantity": cart_item.quantity,
                "street_address": request.data.get("street_address"),
                "city": request.data.get("city"),
                "postal_code": request.data.get("postal_code"),
                "phone_number": request.data.get("phone_number"),
                "status": "PENDING"
            }
            serializer = OrderSerializer(data=order_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            created_orders.append(order)

        # Clear the cart after creating orders
        cart_items.delete()

        return Response(OrderSerializer(created_orders, many=True).data, status=status.HTTP_201_CREATED)
