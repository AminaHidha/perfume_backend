from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.title",
        read_only=True
    )

    product_price = serializers.DecimalField(
        source="product.price",
        read_only=True,
        max_digits=10,
        decimal_places=2
    )

    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_title",
            "product_price",
            "product_image",   # ✅ added
            "quantity",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")
        image = getattr(obj.product, "image", None)

        if not image:
            return None

        # ImageField -> .url
        url = image.url if hasattr(image, "url") else str(image)

        # return absolute URL for frontend
        if request:
            return request.build_absolute_uri(url)

        return url


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items"]
