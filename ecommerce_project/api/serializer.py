from rest_framework import serializers
from api import models
from django.utils.text import slugify

class UserSerializer(serializers.ModelSerializer):
    """Serializes a user object"""

    class Meta:
        model = models.User
        fields = ('id', 'email', 'name', 'password','role')
        extra_kwargs = {
            'password': 
            {
                'write_only': True,
                'style': {'input_type': 'password'},
                'min_length': 8
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""
        user = models.User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data['role'],
        )

        return user
    
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
    class Meta:
        model = models.Product
        fields = '__all__'



class CartSerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'product', 'quantity', 'total_cost']
        extra_kwargs = {
            'user': {'read_only': True}  # Make the user field read-only
        }

    def create(self, validated_data):
        """Create and return a new cart item"""
        cart = models.Cart.objects.create(
            user=self.context['request'].user,  # Assign the authenticated user
            product=validated_data['product'],
            quantity=validated_data['quantity']
        )
        return cart

    def update(self, instance, validated_data):
        """Update and return an existing cart item"""
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