from django.contrib import admin

# Register your models here.
from .models import City, Customer, Product, Category, Brand, State, User, ProfileFeedItem

# Register your models here.
admin.site.register(User)
admin.site.register(ProfileFeedItem)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'is_featured')
    list_filter = ('parent_category', 'is_featured')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name')
    search_fields = ('name', 'abbreviation')
    ordering = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    search_fields = ('name', 'state__name')
    list_filter = ('state',)
    ordering = ('state', 'name')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'city', 'state', 'country', 'zip_code', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'city__name', 'state__name', 'country')
    list_filter = ('state', 'city', 'country', 'date_joined')
    ordering = ('last_name', 'first_name')
