from django.contrib import admin
from rest_framework.authtoken.models import Token
from .models import City, Product, Category, Brand, State, ProfileFeedItem, CustomUser, Cart, Order, CustomToken


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ProfileFeedItem)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Cart)
admin.site.register(Order)

admin.site.register(CustomToken)