from django.core.cache import caches
import json

# Get the product cache
product_cache = caches['product_cache']

def get_cache_key(user_id, product_id=None):
    """
    Generate a cache key for a product or list of products.
    
    Args:
        user_id: The ID of the user who owns the product(s)
        product_id: The ID of the specific product, or None for all user products
        
    Returns:
        str: A cache key string
    """
    if product_id:
        return f"user:{user_id}:product:{product_id}"
    return f"user:{user_id}:products"

def invalidate_product_cache(user_id, product_id):
    """
    Invalidate cache for a specific product and the user's product list.
    
    Args:
        user_id: The ID of the user who owns the product
        product_id: The ID of the specific product
    """
    # Delete both caches
    product_cache.delete(get_cache_key(user_id))
    product_cache.delete(get_cache_key(user_id, product_id))
