from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wishlist
from .serializers import WishlistSerializer


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    def post(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        wishlist.products.add(product_id)
        return Response({'message': 'Added to wishlist'})

    def delete(self, request):
        wishlist = Wishlist.objects.get(user=request.user)
        product_id = request.data.get('product')
        wishlist.products.remove(product_id)
        return Response({'message': 'Removed from wishlist'})
