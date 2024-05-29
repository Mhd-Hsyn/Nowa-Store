# Generated by Django 5.0.6 on 2024-05-29 18:02

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("adminapi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_at", models.DateTimeField(auto_now=True, null=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("text", models.TextField(blank=True, null=True)),
                ("image", models.ImageField(upload_to="product/brand/")),
            ],
            options={
                "verbose_name": "Brand",
                "verbose_name_plural": "Brands",
            },
        ),
        migrations.CreateModel(
            name="ProductCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_at", models.DateTimeField(auto_now=True, null=True)),
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="product/product_category/"
                    ),
                ),
                (
                    "banner_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="product/banner_image/"
                    ),
                ),
                ("banner_text", models.TextField(blank=True, null=True)),
                ("is_banner", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Product Category",
                "verbose_name_plural": "Product Categories",
            },
        ),
        migrations.AlterField(
            model_name="adminauth",
            name="otp_status",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_at", models.DateTimeField(auto_now=True, null=True)),
                ("name", models.CharField(max_length=250, unique=True)),
                ("stock", models.PositiveIntegerField()),
                ("sold", models.PositiveIntegerField()),
                ("is_available", models.BooleanField(default=True)),
                ("overview", models.TextField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("specification", models.TextField(blank=True, null=True)),
                ("price", models.PositiveIntegerField()),
                (
                    "discounted_price",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "saving",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("is_discount", models.BooleanField(default=False)),
                ("discount_date_start", models.DateTimeField(blank=True, null=True)),
                ("discount_date_end", models.DateTimeField(blank=True, null=True)),
                ("delivery_info", models.TextField(blank=True, null=True)),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="brands_products",
                        to="adminapi.brand",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
    ]
