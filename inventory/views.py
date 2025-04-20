from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .utils.cache_utils import get_cache_key, invalidate_product_cache, product_cache
import json
import logging
from .permissions import IsOwner

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
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        """
        This view should return a list of all products
        for the currently authenticated user.
        """
        logger.info(f"Getting queryset for user: {self.request.user.id}")
        return Product.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        List all products with caching and pagination.
        """
        user_id = request.user.id
        # Include pagination parameters in cache key
        page = request.query_params.get('page', '1')
        page_size = request.query_params.get('page_size', str(getattr(self.paginator, 'page_size', 10)))
        cache_key = get_cache_key(user_id, list_view=True, page=page, page_size=page_size)
        
        # Try to get from cache
        cached_data = product_cache.get(cache_key)
        
        if cached_data:
            # Return cached data
            cache_logger.info(f"Cache HIT for list: useddr {user_id}, page {page}, page_size {page_size}")
            return Response(json.loads(cached_data))
        
        # If not in cache, get from database with pagination
        cache_logger.info(f"Cache MISS for list: user {user_id}, page {page}, page_size {page_size}")
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            
            # Cache the paginated result
            product_cache.set(cache_key, json.dumps(response_data))
            logger.info(f"Returning paginated response for page {page}")
            return Response(response_data)
            
        # If pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
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
        Create a product and invalidate list caches.
        """
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            user_id = request.user.id
            # Simply invalidate all list caches for this user
            # This is simpler than trying to update all paginated caches
            invalidate_product_cache(user_id, None)
            logger.info(f"Invalidated list caches for user {user_id}")
        
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