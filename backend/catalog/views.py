from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ItemUnit, Product
from .serializers import ItemUnitSerializer, ProductSerializer
from marketplace.serializers import ListingSerializer
from marketplace.models import Listing


@api_view(["GET"])
@permission_classes([AllowAny])
def product_list(request):
    qs = Product.objects.all().order_by("-created_at")
    q = request.query_params.get("q")
    category = request.query_params.get("category")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    return Response(ProductSerializer(qs[:60], many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    listings = Listing.objects.filter(
        unit__product=product, state="ACTIVE"
    ).select_related("unit")
    data = ProductSerializer(product).data
    data["listings"] = ListingSerializer(listings, many=True).data
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def unit_health_card(request, pk):
    """Public Health Card: unit lifecycle + grade + events."""
    try:
        unit = ItemUnit.objects.select_related("product").get(pk=pk)
    except ItemUnit.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(ItemUnitSerializer(unit).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def preloved_list(request):
    """Return active pre-loved listings (source != NEW)."""
    qs = Listing.objects.filter(state="ACTIVE").exclude(source=Listing.Sources.NEW if hasattr(Listing, 'Sources') else "NEW").select_related('unit__product').order_by('-created_at')
    # Allow filters
    category = request.query_params.get('category')
    grade = request.query_params.get('grade')
    q = request.query_params.get('q')
    if category:
        qs = qs.filter(unit__product__category=category)
    if grade:
        qs = qs.filter(unit__grade=grade)
    if q:
        from django.db.models import Q

        qs = qs.filter(Q(unit__product__title__icontains=q) | Q(unit__product__description__icontains=q))
    return Response(ListingSerializer(qs[:60], many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_fitcheck(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        res = ai.fit_check(product.id, product.category)
        return Response(res)
    except Exception:
        return Response({"hint": None})
