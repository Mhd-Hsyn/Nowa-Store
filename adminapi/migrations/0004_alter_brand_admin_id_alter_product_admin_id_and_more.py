# Generated by Django 5.0.6 on 2024-05-30 18:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("adminapi", "0003_brand_admin_id_product_admin_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brand",
            name="admin_id",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="adminapi.adminauth",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="admin_id",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="adminapi.adminauth",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="brand",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="brands_products",
                to="adminapi.brand",
            ),
        ),
        migrations.AlterField(
            model_name="productcategory",
            name="admin_id",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="adminapi.adminauth",
            ),
        ),
    ]
