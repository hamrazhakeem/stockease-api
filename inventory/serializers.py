from rest_framework import serializers
from .models import Product
from django.db import IntegrityError
import re

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def normalize_name(self, name):
        """
        Normalize a product name by:
        1. Converting to lowercase
        2. Removing extra spaces
        3. Removing all spaces
        """
        # Convert to lowercase
        name = name.lower()
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        # Remove all spaces
        name_without_spaces = name.replace(' ', '')
        return name, name_without_spaces
    
    def validate_name(self, value):
        # Normalize the input name
        normalized_name, name_without_spaces = self.normalize_name(value)
        
        # Check if this name already exists for this user
        user = self.context['request'].user
        existing_products = Product.objects.filter(user=user)
        
        if self.instance:  # Update operation
            existing_products = existing_products.exclude(pk=self.instance.pk)
        
        for product in existing_products:
            # Check both the normalized name and the name without spaces
            existing_normalized, existing_without_spaces = self.normalize_name(product.name)
            
            if (normalized_name == existing_normalized or 
                name_without_spaces == existing_without_spaces):
                raise serializers.ValidationError(
                    "You already have a product with this name or a similar name. "
                    "Product names must be unique (ignoring spaces and case)."
                )
        
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
    
    def create(self, validated_data):
        # Associate the product with the current user
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Normalize the name before saving
        name = validated_data.get('name')
        if name:
            # Just normalize spaces, keep original case
            validated_data['name'] = re.sub(r'\s+', ' ', name).strip()
        
        try:
            return super().create(validated_data)
        except IntegrityError:
            # This is a fallback in case the database constraint is hit
            raise serializers.ValidationError(
                {"name": "You already have a product with this name. Product names must be unique."}
            )
    
    def update(self, instance, validated_data):
        # Normalize the name before saving
        name = validated_data.get('name')
        if name:
            # Just normalize spaces, keep original case
            validated_data['name'] = re.sub(r'\s+', ' ', name).strip()
        
        return super().update(instance, validated_data)