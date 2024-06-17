from django.urls import path, include
from .views import CartViewSet, OrderViewSet, RegisterView, LoginView,UserViewSet

from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CategoryListCreateAPIView, CategoryRetrieveUpdateDestroyAPIView, CityListCreateAPIView, CityRetrieveUpdateDestroyAPIView, LoginView, OrderViewSet, ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView, RegisterView, StateListCreateAPIView, StateRetrieveUpdateDestroyAPIView, UserViewSet

router = DefaultRouter()
router.register('users',  UserViewSet)
router.register('carts',  CartViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categories/',  CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/',  CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-retrieve-update-destroy'),

    path('products/',  ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/',  ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-retrieve-update-destroy'),

    path('states/',  StateListCreateAPIView.as_view(), name='state-list-create'),
    path('states/<int:pk>/',  StateRetrieveUpdateDestroyAPIView.as_view(), name='state-retrieve-update-destroy'),

    path('cities/',  CityListCreateAPIView.as_view(), name='city-list-create'),
    path('cities/<int:pk>/',  CityRetrieveUpdateDestroyAPIView.as_view(), name='city-retrieve-update-destroy'),

    path('register/',  RegisterView.as_view(), name='register'),
    path('login/',  LoginView.as_view(), name='login'),
]
