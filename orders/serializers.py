from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from products.models import Products  # adjust if your model name differs


class OrderItemReadSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_title", "product_image", "quantity", "price"]

    def get_product_image(self, obj):
        request = self.context.get("request")
        image = getattr(obj.product, "image", None)
        if not image:
            return None
        url = image.url if hasattr(image, "url") else str(image)
        return request.build_absolute_uri(url) if request else url


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "full_name",
            "phone_number",
            "street_address",
            "city",
            "state",
            "pincode",
            "payment_method",
            "total_price",
            "discount",
            "final_amount",
            "status",
            "created_at",
            "items",
        ]


# ✅ write serializer for creating order
class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "full_name",
            "phone_number",
            "street_address",
            "city",
            "state",
            "pincode",
            "payment_method",
            "items",
        ]

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        order = Order.objects.create(user=user, total_price=0, discount=0, final_amount=0, **validated_data)

        total = 0
        for item in items_data:
            product_id = item["product"]
            qty = item["quantity"]

            product = Products.objects.get(id=product_id)
            price = product.price  # ensure Products has price field

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=price
            )

            total += float(price) * qty

        order.total_price = total
        order.discount = 0
        order.final_amount = total - float(order.discount)
        order.save()

        return order
