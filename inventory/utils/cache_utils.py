from django.core.cache import caches
import json

# Get the product cache
product_cache = caches['product_cache']

def get_cache_key(user_id, product_id=None, list_view=False, page=None, page_size=None):
    """
    Generate a cache key for a product or list of products.
    
    Args:
        user_id: The ID of the user who owns the product(s)
        product_id: The ID of the specific product, or None for all user products
        list_view: Whether this is for a list view (with pagination)
        page: The page number for pagination
        page_size: The page size for pagination
        
    Returns:
        str: A cache key string
    """
    if product_id:
        return f"user:{user_id}:product:{product_id}"
    if list_view and page and page_size:
        return f"user:{user_id}:products:page:{page}:size:{page_size}"
    return f"user:{user_id}:products"

def invalidate_product_cache(user_id, product_id=None):
    """
    Invalidate cache for a specific product and/or the user's product list.
    
    Args:
        user_id: The ID of the user who owns the product
        product_id: The ID of the specific product, or None to only invalidate list caches
    """
    # Delete product detail cache if product_id is provided
    if product_id:
        product_cache.delete(get_cache_key(user_id, product_id))
    
    # Delete the main list cache
    product_cache.delete(get_cache_key(user_id))
    
    # For django-redis backend
    try:
        client = product_cache._client
        keys = client.keys(f"user:{user_id}:products:page:*")
        if keys:
            client.delete(*keys)
    except:
        pass