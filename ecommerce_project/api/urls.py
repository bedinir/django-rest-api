from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
#router.register('users', views.UserViewSet)
router.register('carts', views.CartViewSet)
router.register('orders',views.OrderViewSet)
router.register('brands',views.BrandViewSet)
router.register('states',views.StateViewSet)
router.register('cities',views.CityViewSet)
router.register('categories',views.CategoryViewSet)
router.register('products',views.ProductViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('products/<int:pk>/activate-deactivate/', views.ProductActivateDeactivateView.as_view(), name='product-activate-deactivate'),

    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('login/', views.LoginView.as_view(), name='login')
]
