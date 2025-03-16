from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .utils.cache_utils import get_cache_key, invalidate_product_cache, product_cache
import json
import logging

# Get regular logger for views
logger = logging.getLogger('inventory')
# Get specialized logger for cache operations
cache_logger = logging.getLogger('inventory.cache')

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing products with caching.
    """
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        """
        This view should return a list of all products
        for the currently authenticated user.
        """
        logger.info(f"Getting queryset for user: {self.request.user.id}")
        return Product.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        List all products with caching.
        """
        user_id = request.user.id
        cache_key = get_cache_key(user_id)
        
        # Try to get from cache
        cached_data = product_cache.get(cache_key)
        
        if cached_data:
            # Return cached data
            cache_logger.info(f"Cache HIT for list: user {user_id}")
            return Response(json.loads(cached_data))
        
        # If not in cache, get from database
        cache_logger.info(f"Cache MISS for list: user {user_id}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Cache the result
        product_cache.set(cache_key, json.dumps(serializer.data))
        logger.info("Returning response after retrieving list")
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a product with caching.
        """
        user_id = request.user.id
        product_id = kwargs.get('pk')
        cache_key = get_cache_key(user_id, product_id)
        
        # Try to get from cache
        cached_data = product_cache.get(cache_key)
        
        if cached_data:
            cache_logger.info(f"Cache HIT for product: {product_id}")
            # Return cached data
            return Response(json.loads(cached_data))
        
        # If not in cache, get from database
        cache_logger.info(f"Cache MISS for product: {product_id}")
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the result if successful
        if response.status_code == status.HTTP_200_OK:
            cache_logger.info(f"Caching product: {product_id}")
            product_cache.set(cache_key, json.dumps(response.data))
        
        logger.info("Returning response after retrieving product")
        return response
    
    def create(self, request, *args, **kwargs):
        """
        Create a product and update the list cache if it exists.
        """
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            user_id = request.user.id
            cache_key = get_cache_key(user_id)
            
            # Check if there's an existing cache for the product list
            cached_data = product_cache.get(cache_key)
            
            if cached_data:
                # If cache exists, update it by adding the new product
                product_list = json.loads(cached_data)
                product_list.append(response.data)
                
                cache_logger.info(f"Updating cache for user {user_id}")
                # Update the cache with the new list
                product_cache.set(cache_key, json.dumps(product_list))
        
        logger.info("Returning response after creating product")
        return response
    
    def update(self, request, *args, **kwargs):
        """
        Update a product and invalidate caches.
        """
        user_id = request.user.id
        product_id = kwargs.get('pk')
        
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            cache_logger.info(f"Invalidating caches for user {user_id}")
            print("Invalidating caches")
            # Invalidate both the list cache and the individual product cache
            invalidate_product_cache(user_id, product_id)
        
        logger.info("Returning response after updating product")
        return response
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a product and invalidate caches.
        """
        user_id = request.user.id
        product_id = kwargs.get('pk')
        
        response = super().partial_update(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            cache_logger.info(f"Invalidating caches for user {user_id}")
            # Invalidate both the list cache and the individual product cache
            invalidate_product_cache(user_id, product_id)
        
        logger.info("Returning response after partial updating product")
        return response
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a product and invalidate caches.
        """
        user_id = request.user.id
        product_id = kwargs.get('pk')
        
        response = super().destroy(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            cache_logger.info(f"Invalidating caches for user {user_id}")
            # Invalidate both the list cache and the individual product cache
            invalidate_product_cache(user_id, product_id)
        
        logger.info("Returning response after deleting product")
        return response