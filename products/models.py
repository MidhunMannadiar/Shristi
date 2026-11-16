from django.db import models
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)

    slug = models.SlugField(max_length=120, unique=True)

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=220,
        unique=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField()

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)

    main_image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):

        if self.original_price > self.selling_price:
            discount = (
                (self.original_price - self.selling_price)
                / self.original_price
            ) * 100

            return round(discount)

        return 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )

    image = models.ImageField(
        upload_to="products/gallery/"
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - Gallery Image"

