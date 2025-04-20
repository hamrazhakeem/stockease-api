from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product
from accounts.models import User
from .utils.cache_utils import product_cache, get_cache_key
import json

class ProductAPITestCase(TestCase):
    """Test suite for the Product API with caching."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Test Product 1',
            price=100,
            quantity=10,
            user=self.user
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            price=200,
            quantity=20,
            user=self.user
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Clear cache before each test
        product_cache.clear()
    
    def test_list_products(self):
        """Test retrieving a list of products with pagination."""
        # First request should hit the database
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination structure
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check if data is cached - include pagination params in cache key
        page = '1'
        page_size = '10'  # Default page size
        cache_key = get_cache_key(self.user.id, list_view=True, page=page, page_size=page_size)
        cached_data = product_cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        # Second request should hit the cache
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_product(self):
        """Test retrieving a single product."""
        # First request should hit the database
        response = self.client.get(reverse('product-detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product 1')
        
        # Check if data is cached
        cache_key = get_cache_key(self.user.id, self.product1.id)
        cached_data = product_cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        # Second request should hit the cache
        response = self.client.get(reverse('product-detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product 1')
    
    def test_create_product(self):
        """Test creating a product."""
        # If list was previously cached, check if new product is in updated cache
        cache_key = get_cache_key(self.user.id, list_view=True, page='1', page_size='10')

        # First, manually cache the list
        self.client.get(reverse('product-list'))

        # Then create another product
        another_product_data = {
            'name': 'Another Test Product',
            'price': 400,
            'quantity': 40
        }

        response = self.client.post(
            reverse('product-list'),
            another_product_data,
            format='json'
        )

        # The cache was invalidated by the create operation
        # So we need to reload the cache by making another GET request
        self.client.get(reverse('product-list'))

        # Now get the cached list
        cached_data = product_cache.get(cache_key)
        cached_response = json.loads(cached_data)
        cached_list = cached_response['results']

        # Verify the number of products
        self.assertEqual(cached_response['count'], 4)
        # Verify the new product is in the cached list
        self.assertTrue(any(item['name'] == 'Another Test Product' for item in cached_list))
    
    def test_update_product(self):
        """Test updating a product invalidates cache."""
        # First, cache the product
        self.client.get(reverse('product-detail', args=[self.product1.id]))
        
        # Update the product
        updated_data = {
            'name': 'Updated Test Product',
            'price': 150,
            'quantity': 15
        }
        
        response = self.client.put(
            reverse('product-detail', args=[self.product1.id]),
            updated_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if cache was invalidated
        cache_key = get_cache_key(self.user.id, self.product1.id)
        cached_data = product_cache.get(cache_key)
        self.assertIsNone(cached_data)
        
        # List cache should also be invalidated
        list_cache_key = get_cache_key(self.user.id)
        list_cached_data = product_cache.get(list_cache_key)
        self.assertIsNone(list_cached_data)
    
    def test_delete_product(self):
        """Test deleting a product invalidates cache."""
        # First, cache the product list
        self.client.get(reverse('product-list'))
        
        # Delete a product
        response = self.client.delete(reverse('product-detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check if list cache was invalidated
        cache_key = get_cache_key(self.user.id)
        cached_data = product_cache.get(cache_key)
        self.assertIsNone(cached_data)
        
        # Verify the product was deleted from the database
        self.assertEqual(Product.objects.count(), 1)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access products."""
        # Create another user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword123'
        )
        
        # Create a product for the other user
        other_product = Product.objects.create(
            name='Other User Product',
            price=500,
            quantity=50,
            user=other_user
        )
        
        # Try to access the other user's product
        response = self.client.get(reverse('product-detail', args=[other_product.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
