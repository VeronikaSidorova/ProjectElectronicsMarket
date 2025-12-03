from rest_framework import serializers
from .models import Contact, Product, NetworkNode


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class NetworkNodeSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.ReadOnlyField()

    class Meta:
        model = NetworkNode
        fields = "__all__"
        read_only_fields = ["debt", "created_at"]


class NetworkNodeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkNode
        fields = "__all__"
        read_only_fields = ["debt", "created_at"]


class NetworkNodeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkNode
        exclude = ["debt"]
        read_only_fields = ["created_at"]
