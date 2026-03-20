from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    price = serializers.ReadOnlyField(source='product.price')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        total = 0
        for item in obj.items.all():
            if item.product.price:
                total += item.product.price * item.quantity
        return total

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'