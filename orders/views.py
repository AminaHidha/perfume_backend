from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderReadSerializer, OrderCreateSerializer

# ✅ add these imports
from cart.models import Cart, CartItem


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderReadSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            order = Order.objects.get(id=id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderReadSerializer(order, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()

            # ✅ CLEAR CART ITEMS AFTER ORDER
            try:
                cart = Cart.objects.get(user=request.user)

                items = request.data.get("items", [])
                from_cart = request.data.get("from_cart", False)

                if from_cart:
                    # ✅ if checkout from cart → clear entire cart
                    CartItem.objects.filter(cart=cart).delete()
                else:
                    # ✅ if buy-now → remove only ordered products (if they exist in cart)
                    product_ids = [it.get("product") for it in items if it.get("product")]
                    if product_ids:
                        CartItem.objects.filter(cart=cart, product_id__in=product_ids).delete()

            except Cart.DoesNotExist:
                pass

            return Response(
                OrderReadSerializer(order, context={"request": request}).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
