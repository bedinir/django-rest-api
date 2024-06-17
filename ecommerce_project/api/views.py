from rest_framework import generics, filters, viewsets
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from api import models
from api import permissions
from api import serializer

class UserViewSet(viewsets.ModelViewSet):
    """Handle creating and updating users"""
    serializer_class = serializer.UserSerializer
    queryset = models.User.objects.all()
    # 1
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsAdmin)
    # 2
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)
class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


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




class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializer.CategorySerializer

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializer.CategorySerializer

class BrandListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.Brand.objects.all()
    serializer_class = serializer.BrandSerializer

class BrandRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Brand.objects.all()
    serializer_class = serializer.BrandSerializer

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductSerializer

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductSerializer

class StateListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.State.objects.all()
    serializer_class = serializer.StateSerializer

class StateRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.State.objects.all()
    serializer_class = serializer.StateSerializer

class CityListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.City.objects.all()
    serializer_class = serializer.CitySerializer

class CityRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.City.objects.all()
    serializer_class = serializer.CitySerializer

# class CustomerListCreateAPIView(generics.ListCreateAPIView):
#     queryset = models.Customer.objects.all()
#     serializer_class = serializer.CustomerSerializer

# class CustomerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = models.Customer.objects.all()
#     serializer_class = serializer.CustomerSerializer


class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializer.CartSerializer
    queryset = models.Cart.objects.all()

    permission_classes = (IsAuthenticated, permissions.IsOwner, permissions.IsCustomer)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializer.OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, permissions.IsOwner, permissions.IsCustomer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)