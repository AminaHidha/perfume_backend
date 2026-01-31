from rest_framework.viewsets import ModelViewSet
from .models import Products, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.permissions import AllowAny, IsAdminUser



class ProductViewSet(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        # Public access for GET requests
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]

        # Admin only for create/update/delete
        return [IsAdminUser()]
    
    
class CategoryViewSet(ModelViewSet):
    """
    Category CRUD (Admin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
