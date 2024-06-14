from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-retrieve-update-destroy'),

    path('brands/', views.BrandListCreateAPIView.as_view(), name='brand-list-create'),
    path('brands/<int:pk>/', views.BrandRetrieveUpdateDestroyAPIView.as_view(), name='brand-retrieve-update-destroy'),

    path('products/', views.ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-retrieve-update-destroy'),

    path('states/', views.StateListCreateAPIView.as_view(), name='state-list-create'),
    path('states/<int:pk>/', views.StateRetrieveUpdateDestroyAPIView.as_view(), name='state-retrieve-update-destroy'),

    path('cities/', views.CityListCreateAPIView.as_view(), name='city-list-create'),
    path('cities/<int:pk>/', views.CityRetrieveUpdateDestroyAPIView.as_view(), name='city-retrieve-update-destroy'),

    path('customers/', views.CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', views.CustomerRetrieveUpdateDestroyAPIView.as_view(), name='customer-retrieve-update-destroy'),
]
