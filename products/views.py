
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Category
from .forms import CategoryForm
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageFormSet
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils.http import url_has_allowed_host_and_scheme

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("accounts:admin_login")

        if not request.user.is_admin:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper




@admin_required
def category_list(request):

    categories = Category.objects.all()

    # SEARCH
    search_query = request.GET.get("search", "").strip()

    if search_query:
        categories = categories.filter(
            name__icontains=search_query
        )

    # FILTER AND SORTING
    filter_option = request.GET.get("filter", "")

    if filter_option == "active":
        categories = categories.filter(is_active=True)
        categories = categories.order_by("-created_at")

    elif filter_option == "inactive":
        categories = categories.filter(is_active=False)
        categories = categories.order_by("-created_at")

    elif filter_option == "name_asc":
        categories = categories.order_by("name")

    elif filter_option == "name_desc":
        categories = categories.order_by("-name")

    elif filter_option == "date_asc":
        categories = categories.order_by("created_at")

    else:
        categories = categories.order_by("-created_at")
        if filter_option != "date_desc":
            filter_option = "date_desc"

    # PAGINATION
    per_page = request.GET.get("per_page", "10")

    allowed_per_page = [5, 10, 15, 20, 25, 50]

    try:
        per_page = int(per_page)
    except (ValueError, TypeError):
        per_page = 10

    if per_page not in allowed_per_page:
        per_page = 10

    paginator = Paginator(categories, per_page)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "categories": page_obj.object_list,
        "page_obj": page_obj,
        "search_query": search_query,
        "filter_option": filter_option,
        "per_page": per_page,
        "allowed_per_page": allowed_per_page,
    }

    return render(
        request,
        "admin/categories/category_list.html",
        context
    )



@admin_required
def category_create(request):

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Category created successfully."
            )

            return redirect("products:category_list")

    else:
        form = CategoryForm()

    return render(
        request,
        "admin/categories/category_form.html",
        {
            "form": form,
            "page_title": "Add Category",
        }
    )


@admin_required
def category_update(request, pk):

    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES,
            instance=category
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Category updated successfully."
            )

            return redirect("products:category_list")

    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "admin/categories/category_form.html",
        {
            "form": form,
            "page_title": "Edit Category",
            "category": category,
        }
    )

@admin_required
@require_POST
def category_remove_image(request, pk):

    category = get_object_or_404(Category, pk=pk)

    if category.image:

        # Store the existing image information
        image_storage = category.image.storage
        image_name = category.image.name

        # Remove the image reference from the category
        category.image = ""
        category.save(update_fields=["image"])

        # Delete the physical image after the database update commits
        def delete_category_image():
            if image_storage.exists(image_name):
                image_storage.delete(image_name)

        transaction.on_commit(delete_category_image)

        messages.success(
            request,
            "Category image removed successfully."
        )

    return redirect(
        "products:category_update",
        pk=category.pk
    )



@admin_required
def category_delete(request, pk):

    category = get_object_or_404(Category, pk=pk)

    # Get all products belonging to this category
    products = list(
        category.products.prefetch_related("gallery_images").all()
    )

    # Display the confirmation page
    if request.method == "GET":

        return render(
            request,
            "admin/categories/category_confirm_delete.html",
            {
                "category": category,
                "products": products,
                "product_count": len(products),
            }
        )

    # Only allow POST for actual deletion
    if request.method != "POST":
        return redirect("products:category_list")

    # Require explicit confirmation
    if request.POST.get("confirm_delete") != "yes":
        messages.error(
            request,
            "Please confirm the category deletion."
        )
        return redirect("products:category_list")

    # Collect uploaded files before deleting database records
    image_files = []

    if category.image:
        image_files.append(
            (category.image.storage, category.image.name)
        )

    for product in products:

        if product.main_image:
            image_files.append(
                (product.main_image.storage, product.main_image.name)
            )

        for gallery_image in product.gallery_images.all():

            if gallery_image.image:
                image_files.append(
                    (gallery_image.image.storage, gallery_image.image.name)
                )

    try:

        with transaction.atomic():

            # Explicitly delete associated products
            for product in products:
                product.delete()

            # Delete the category after its products
            category.delete()

            # Delete uploaded files only after successful DB commit
            def delete_uploaded_files():

                for storage, name in image_files:

                    if storage.exists(name):
                        storage.delete(name)

            transaction.on_commit(delete_uploaded_files)

        messages.success(
            request,
            "Category and all its associated products "
            "were deleted successfully."
        )

    except ProtectedError:

        messages.error(
            request,
            "Deletion was blocked because one or more products "
            "are referenced by other records. "
            "The category and products have not been deleted."
        )

    return redirect("products:category_list")




@admin_required
def product_list(request):

    products = Product.objects.select_related(
        "category"
    )

    # SEARCH
    search_query = request.GET.get("search", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    # STOCK FILTER
    stock = request.GET.get("stock", "")

    if stock == "in_stock":
        products = products.filter(stock__gt=0)

    elif stock == "out_of_stock":
        products = products.filter(stock=0)

    # PRODUCT STATUS FILTER
    status = request.GET.get("status", "")

    if status == "active":
        products = products.filter(is_active=True)

    elif status == "inactive":
        products = products.filter(is_active=False)

    # SORTING
    sort = request.GET.get("sort", "newest")

    if sort == "oldest":
        products = products.order_by("created_at")

    elif sort == "name_asc":
        products = products.order_by("name")

    elif sort == "name_desc":
        products = products.order_by("-name")

    else:
        products = products.order_by("-created_at")
        sort = "newest"

    # PAGINATION
    per_page = request.GET.get("per_page", "5")

    allowed_per_page = [5, 10, 15, 20, 25, 50]

    try:
        per_page = int(per_page)
    except (ValueError, TypeError):
        per_page = 5

    if per_page not in allowed_per_page:
        per_page = 5

    paginator = Paginator(products, per_page)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "products": page_obj,
        "search_query": search_query,
        "stock": stock,
        "status": status,
        "sort": sort,
        "per_page": per_page,
        "allowed_per_page": allowed_per_page,
    }

    return render(
        request,
        "admin/products/product_list.html",
        context
    )


@admin_required
def product_create(request):

    if request.method == "POST":

        product_form = ProductForm(
            request.POST,
            request.FILES
        )

        image_formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            queryset=ProductImage.objects.none()
        )

        if product_form.is_valid() and image_formset.is_valid():

            product = product_form.save()

            gallery_images = image_formset.save(commit=False)

            for image in gallery_images:
                image.product = product
                image.save()

            return redirect("products:product_list")

    else:

        product_form = ProductForm()

        image_formset = ProductImageFormSet(
            queryset=ProductImage.objects.none()
        )

    context = {
        "form": product_form,
        "image_formset": image_formset,
        "page_title": "Add New Product",
    }

    return render(
        request,
        "admin/products/product_form.html",
        context
    )



@admin_required
def product_update(request, pk):

    product = get_object_or_404(Product, pk=pk)

    # Preserve the category confirmation page URL
    return_to = (
        request.POST.get("return_to")
        or request.GET.get("return_to", "")
    )

    # Allow only safe URLs within this website
    if return_to and not url_has_allowed_host_and_scheme(
        return_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        return_to = ""

    if request.method == "POST":

        product_form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        image_formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            queryset=product.gallery_images.all()
        )

        if product_form.is_valid() and image_formset.is_valid():

            product_form.save()

            gallery_images = image_formset.save(commit=False)

            for image in gallery_images:
                image.product = product
                image.save()

            # Collect gallery image files before deleting their records
            deleted_image_files = []

            for image in image_formset.deleted_objects:

                if image.image:
                    deleted_image_files.append(
                        (image.image.storage, image.image.name)
                    )

                image.delete()

            # Delete physical files after database transaction commits
            def delete_gallery_files():

                for storage, name in deleted_image_files:

                    if storage.exists(name):
                        storage.delete(name)

            transaction.on_commit(delete_gallery_files)

            messages.success(
                request,
                "Product updated successfully."
            )

            # Return to the category confirmation page if requested
            if return_to:
                return redirect(return_to)

            return redirect("products:product_list")

    else:

        product_form = ProductForm(instance=product)

        image_formset = ProductImageFormSet(
            queryset=product.gallery_images.all()
        )

    context = {
        "form": product_form,
        "image_formset": image_formset,
        "page_title": "Edit Product",
        "product": product,
        "return_to": return_to,
    }

    return render(
        request,
        "admin/products/product_form.html",
        context
    )



@admin_required
def product_delete(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        # Collect the main image before deleting the product
        image_files = []

        if product.main_image:
            image_files.append(
                (product.main_image.storage, product.main_image.name)
            )

        # Collect all gallery images
        for gallery_image in product.gallery_images.all():

            if gallery_image.image:
                image_files.append(
                    (gallery_image.image.storage, gallery_image.image.name)
                )

        # Delete product and related database records
        product.delete()

        # Delete uploaded files only after database commit
        def delete_uploaded_files():

            for storage, name in image_files:

                if storage.exists(name):
                    storage.delete(name)

        transaction.on_commit(delete_uploaded_files)

        return redirect("products:product_list")

    context = {
        "product": product
    }

    return render(
        request,
        "admin/products/product_confirm_delete.html",
        context
    )