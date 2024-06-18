from api import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils.text import slugify

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            data['user'] = user
            data['token'], created = Token.objects.get_or_create(user=user)
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        return data
    
class ProfileFeedItemSerializer(serializers.ModelSerializer):
    """Serializes profile feed items"""

    class Meta:
        model = models.ProfileFeedItem
        fields = ('id', 'user_profile', 'status_text', 'created_on')
        extra_kwargs = {'user_profile': {'read_only': True}}


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    state = serializers.CharField(write_only=True)

    class Meta:
        model = models.City
        fields = '__all__'

    def create(self, validated_data):
        state_abbreviation = validated_data.pop('state')
        try:
            state = models.State.objects.get(abbreviation=state_abbreviation)
        except models.State.DoesNotExist:
            raise serializers.ValidationError(f"State with abbreviation '{state_abbreviation}' does not exist.")
        
        city = models.City.objects.create(state=state, **validated_data)
        return city
    
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = '__all__'
        
class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True) 

    class Meta:
        model = models.Category
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        # Auto-generate slug if not provided
        if 'slug' not in validated_data or not validated_data['slug']:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Auto-generate slug if not provided
        if 'slug' not in validated_data or not validated_data['slug']:
            validated_data['slug'] = slugify(validated_data.get('name', instance.name))
        return super().update(instance, validated_data)



class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all(), source='category', write_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(queryset=models.Brand.objects.all(), source='brand', write_only=True)
    class Meta:
        model = models.Product
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at','is_active'] 

    # Ensure discount_price is less than price if provided
    def validate(self, data):
        price = data.get('price')
        discount_price = data.get('discount_price')
        if discount_price and discount_price >= price:
            raise serializers.ValidationError("Discount price must be less than the regular price.")
        return data

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        brand_id = validated_data.pop('brand_id')

        try:
            category = models.Category.objects.get(id=category_id)
        except  models.Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID.")

        try:
            brand =  models.Brand.objects.get(id=brand_id)
        except  models.Brand.DoesNotExist:
            raise serializers.ValidationError("Invalid brand ID.")

        product =  models.Product.objects.create(category=category, brand=brand, **validated_data)
        return product

    def update(self, instance, validated_data):
        if not instance.is_active:
            raise serializers.ValidationError("Cannot update an inactive product.")
        
        category_id = validated_data.pop('category_id', None)
        brand_id = validated_data.pop('brand_id', None)

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.discount_price = validated_data.get('discount_price', instance.discount_price)
        instance.stock_quantity = validated_data.get('stock_quantity', instance.stock_quantity)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        if category_id:
            try:
                category =  models.Category.objects.get(id=category_id)
                instance.category = category
            except  models.Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID.")

        if brand_id:
            try:
                brand =  models.Brand.objects.get(id=brand_id)
                instance.brand = brand
            except  models.Brand.DoesNotExist:
                raise serializers.ValidationError("Invalid brand ID.")

        instance.save()
        return instance
class ProductActivationSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

class CartSerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField(source='get_total_cost')

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'product', 'quantity', 'total_cost']
        extra_kwargs = {
            'user': {'read_only': True}  # Make the user field read-only
        }

    def create(self, validated_data):
        cart = models.Cart.objects.create(
            user=self.context['request'].user,  # Assign the authenticated user
            product=validated_data['product'],
            quantity=validated_data['quantity']
        )
        return cart

    def update(self, instance, validated_data):
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = models.Order
        fields = ['id', 'user', 'product', 'quantity', 'status', 'total_cost', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True},  # Make the user field read-only
            'status': {'read_only': True},  # Optionally make status read-only on creation
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def create(self, validated_data):
        """Create and return a new order"""
        order = models.Order.objects.create(
            user=self.context['request'].user,  # Assign the authenticated user
            product=validated_data['product'],
            quantity=validated_data['quantity']
        )
        return order

    def update(self, instance, validated_data):
        """Update and return an existing order"""
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance