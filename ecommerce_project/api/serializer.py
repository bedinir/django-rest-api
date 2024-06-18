from api import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils.text import slugify
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True},'role': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
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

            try:
                token, created = Token.objects.get_or_create(user=user)
                data['token'] = token.key
            except IntegrityError as e:
                raise serializers.ValidationError('Error creating token') from e

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
    category = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=models.Brand.objects.all())

    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'description', 'category', 'category_name', 'brand','brand_name', 'price', 'discount_price', 'stock_quantity', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at','is_active'] 

    # Ensure discount_price is less than price if provided
    def validate(self, data):
        price = data.get('price')
        discount_price = data.get('discount_price')
        if discount_price and discount_price >= price:
            raise serializers.ValidationError("Discount price must be less than the regular price.")
        return data

    def create(self, validated_data):
        category = validated_data.pop('category')
        brand = validated_data.pop('brand')
        try:
            x = models.Category.objects.get(name=category)
        except  models.Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID.")

        try:
            y =  models.Brand.objects.get(name=brand)
        except  models.Brand.DoesNotExist:
            raise serializers.ValidationError("Invalid brand ID.")

        product =  models.Product.objects.create(category=category, brand=brand, **validated_data)
        return product

    def update(self, instance, validated_data):
        if not instance.is_active:
            raise serializers.ValidationError("Cannot update an inactive product.")
        
        category= validated_data.pop('category', None)
        brand = validated_data.pop('brand', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category:
            try:
                x =  models.Category.objects.get(name=category)
                instance.category = x
            except  models.Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID.")

        if brand:
            try:
                y =  models.Brand.objects.get(name=brand)
                instance.brand = y
            except  models.Brand.DoesNotExist:
                raise serializers.ValidationError("Invalid brand ID.")

        instance.save()
        return instance
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False  # Soft delete by marking as inactive
            instance.save()
            return Response({"message": f"Product '{instance.name}' has been deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Product is already inactive."}, status=status.HTTP_404_NOT_FOUND)
class ProductActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['is_active']

class CartSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()
    product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    pr_name = serializers.CharField(source='product.name', read_only=True)
    pr_price= serializers.DecimalField(source='product.price',max_digits=10, decimal_places=2, read_only=True)
    pr_discount_price= serializers.DecimalField(source='product.discount_price',max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'product', 'pr_name','pr_price','pr_discount_price','quantity', 'total_cost']
        extra_kwargs = {
            'user': {'read_only': True}  # Make the user field read-only
        }
    def get_total_cost(self, obj):
        return obj.total_cost
    def create(self, validated_data):
        product = validated_data.pop('product')
        try:
            p = models.Product.objects.get(name=product)
        except models.Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")
        
        if p.is_active == False:
            raise serializers.ValidationError(f"This product is inactive, please choose a new one!")

        if p.stock_quantity < validated_data.get('quantity',1):
            raise serializers.ValidationError(f"Insufficient stock for product ID {product}. Available stock: {p.stock_quantity}.")


        cart =  models.Cart.objects.create(user=self.context['request'].user, 
            product=product, **validated_data)
      
        return cart

    def update(self, instance, validated_data):
        product = validated_data.pop('product')

        try:
            p = models.Product.objects.get(pk=product.pk)  # Use pk instead of name
        except models.Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")
        
        if not p.is_active:
            raise serializers.ValidationError(f"The product '{p.name}' is inactive, please choose a different one!")

        if p.stock_quantity < validated_data.get('quantity', instance.quantity):
            raise serializers.ValidationError(f"Insufficient stock for product '{p.name}'. Available stock: {p.stock_quantity}.")

        instance.product = product
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance 
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.delete()
            return Response({"message": f"Cart item ID {instance.id} has been deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

class OrderSerializer(serializers.ModelSerializer):
   city = serializers.PrimaryKeyRelatedField(queryset=models.City.objects.all())
   product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())
   state = serializers.SerializerMethodField() 
   total_cost = serializers.SerializerMethodField()
   
   class Meta:
        model = models.Order
        fields = '__all__'  
        extra_kwargs = {
            'user': {'read_only': True},  
            'status': {'read_only': True},  
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'state':{'read_only': True},
        }
   def get_state(self, obj):
        return obj.city.state.id if obj.city else None
   def get_total_cost(self, obj):
        return obj.total_cost
   def validate(self, data):
        required_fields = ['street_address', 'city', 'postal_code', 'phone_number']
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(f"{field} is required.")

        return data

   def create(self, validated_data):
        city = validated_data.pop('city')
        product = validated_data.pop('product')

        
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("User context is missing.")
        user = request.user
        validated_data['user'] = user
        try:
            c = models.City.objects.get(name=city)
        except models.City.DoesNotExist:
            raise serializers.ValidationError("Invalid city ID.")
        
        try:
            p = models.Product.objects.get(name=product)
        except models.Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")
        
        if p.is_active == False:
            raise serializers.ValidationError(f"This product is inactive, please choose a new one!")

        if p.stock_quantity < validated_data.get('quantity',1):
            raise serializers.ValidationError(f"Insufficient stock for product ID {product}. Available stock: {p.stock_quantity}.")

        state = c.state

        order = models.Order.objects.create(
            city=city,
            state=state,
            product=product,
            **validated_data
        )

        return order
   
   def update(self, instance, validated_data):
        if instance.status != 'PENDING':
            raise serializers.ValidationError("Only orders with status 'PENDING' can be updated.")

        city = validated_data.pop('city')
        product = validated_data.pop('product')

        try:
            c = models.City.objects.get(pk=city.pk)
            instance.city = c
            instance.state = c.state
        except models.City.DoesNotExist:
            raise serializers.ValidationError("Invalid city ID.")

        try:
            p = models.Product.objects.get(pk=product.pk)
            instance.product = p
            if not p.is_active:
                raise serializers.ValidationError(f"This product '{p.name}' is inactive, please choose a different one!")
            if p.stock_quantity < validated_data.get('quantity', instance.quantity):
                raise serializers.ValidationError(f"Insufficient stock for product '{p.name}'. Available stock: {p.stock_quantity}.")
        except models.Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance