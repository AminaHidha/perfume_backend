from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Products  # adjust if your product model name/path differs


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # ✅ pass request context for absolute image URLs
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
          return Response({"error": "Product is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({"error": "Quantity must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity == 0:
            return Response({"error": "Quantity cannot be 0."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ ensure product exists
        product = get_object_or_404(Products, id=product_id)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            # if new item, initial quantity must be positive
            if quantity < 1:
                return Response(
                    {"error": "Quantity must be at least 1 for a new item."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            item.quantity = quantity
            item.save()
        else:
            # existing item: allow +1, -1 updates
            item.quantity += quantity

            if item.quantity <= 0:
                item.delete()
            else:
                item.save()

        # ✅ return updated cart
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
