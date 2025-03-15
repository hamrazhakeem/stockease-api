from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing products.
    """
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        """
        This view should return a list of all products
        for the currently authenticated user.
        """
        return Product.objects.filter(user=self.request.user)