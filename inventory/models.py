from django.db import models
from accounts.models import User

# Create your models here.

class Product(models.Model):  # Use singular 'Product' for the model
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name