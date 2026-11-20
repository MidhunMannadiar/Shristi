
from django.shortcuts import render, get_object_or_404
from products.models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse

def home(request):
    categories = Category.objects.filter(
        is_active=True
    ).order_by("-created_at")[:4]

    context = {
        "categories": categories,
    }

    return render(request, "storefront/home.html", context)



def shop(request):
    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related("category")

    # Search products and categories
    search_query = request.GET.get("q", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Sorting options
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_low": "selling_price",
        "price_high": "-selling_price",
        "name_az": "name",
        "name_za": "-name",
    }

    sort_by = request.GET.get("sort", "newest")

    if sort_by not in sort_options:
        sort_by = "newest"

    products = products.order_by(sort_options[sort_by])

    # Active categories
    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    # Category filtering
    selected_categories = request.GET.getlist("category")

    if selected_categories:
        products = products.filter(
            category__id__in=selected_categories
        )

    # Price filtering
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")

    if min_price:
        products = products.filter(
            selling_price__gte=min_price
        )

    if max_price:
        products = products.filter(
            selling_price__lte=max_price
        )

    # Products per page
    per_page_options = [5, 10, 20, 30]

    try:
        per_page = int(request.GET.get("per_page", 5))
    except (ValueError, TypeError):
        per_page = 5

    if per_page not in per_page_options:
        per_page = 5

    # Availability filtering
    availability = request.GET.get("availability", "")

    if availability == "in_stock":
        products = products.filter(stock__gt=0)

    elif availability == "out_of_stock":
        products = products.filter(stock=0)

    # Pagination
    paginator = Paginator(products, per_page)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "categories": categories,
        "page_obj": page_obj,
        "per_page": per_page,
        "per_page_options": per_page_options,
        "sort_by": sort_by,
        "sort_options": sort_options,
        "selected_categories": selected_categories,
        "min_price": min_price,
        "max_price": max_price,
        "availability": availability,
        "search_query": search_query,
    }

    return render(request, "storefront/shop.html", context)

def search_suggestions(request):

    query = request.GET.get("q", "").strip()

    # Return empty results for short searches
    if len(query) < 2:
        return JsonResponse({"results": []})

    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(sku__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related(
        "category"
    ).distinct().order_by(
        "name"
    )[:5]

    results = []

    for product in products:

        results.append({
            "name": product.name,
            "price": str(product.selling_price),
            "image": (
                product.main_image.url
                if product.main_image
                else ""
            ),
            "url": reverse(
                "storefront:product_detail",
                kwargs={"slug": product.slug}
            ),
        })

    return JsonResponse({
        "results": results
    })



def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
        category__is_active=True
    )

    gallery_images = product.gallery_images.all()

    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        category__is_active=True
    ).exclude(
        id=product.id
    ).order_by("-created_at")[:3]

    context = {
        "product": product,
        "gallery_images": gallery_images,
        "similar_products": similar_products,
    }

    return render(request, "storefront/product_detail.html", context)
