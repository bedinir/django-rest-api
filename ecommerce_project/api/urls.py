from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
# router.register('users', views.UserViewSet)
# router.register('carts', views.CartViewSet)
# router.register('orders',views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('categories/', views.CategoryListCreateAPIView.as_view(), name='category-list-create'),
    # path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-retrieve-update-destroy'),

    # path('brands/', views.BrandListCreateAPIView.as_view(), name='brand-list-create'),
    # path('brands/<int:pk>/', views.BrandRetrieveUpdateDestroyAPIView.as_view(), name='brand-retrieve-update-destroy'),

    # path('products/', views.ProductListCreateAPIView.as_view(), name='product-list-create'),
    # path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-retrieve-update-destroy'),

    # path('states/', views.StateListCreateAPIView.as_view(), name='state-list-create'),
    # path('states/<int:pk>/', views.StateRetrieveUpdateDestroyAPIView.as_view(), name='state-retrieve-update-destroy'),

    # path('cities/', views.CityListCreateAPIView.as_view(), name='city-list-create'),
    # path('cities/<int:pk>/', views.CityRetrieveUpdateDestroyAPIView.as_view(), name='city-retrieve-update-destroy'),

    # path('customers/', views.CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    # path('customers/<int:pk>/', views.CustomerRetrieveUpdateDestroyAPIView.as_view(), name='customer-retrieve-update-destroy'),
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
