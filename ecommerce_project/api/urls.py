from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('carts', views.CartViewSet)
router.register('orders',views.OrderViewSet)
router.register('brands',views.BrandViewSet)
router.register('states',views.StateViewSet)
router.register('cities',views.CityViewSet)
router.register('categories',views.CategoryViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    
    path('products/', views.ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-retrieve-update-destroy'),
]
