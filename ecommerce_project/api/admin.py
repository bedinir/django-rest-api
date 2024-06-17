from django.contrib import admin

# Register your models here.
from .models import City, Product, Category, Brand, State, User, ProfileFeedItem

# Register your models here.
admin.site.register(User)
admin.site.register(ProfileFeedItem)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(State)
admin.site.register(City)
