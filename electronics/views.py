from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Contact, Product, NetworkNode
from .serializers import (
    ContactSerializer,
    ProductSerializer,
    NetworkNodeSerializer,
    NetworkNodeCreateSerializer,
    NetworkNodeUpdateSerializer,
)
from .permissions import IsActiveEmployee


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["country"]
    search_fields = ["country", "city"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "model"]


class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = (
        NetworkNode.objects.all()
        .select_related("contact", "supplier")
        .prefetch_related("products")
    )
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["contact__country"]
    search_fields = ["name", "contact__city"]

    def get_serializer_class(self):
        if self.action == "create":
            return NetworkNodeCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return NetworkNodeUpdateSerializer
        return NetworkNodeSerializer
