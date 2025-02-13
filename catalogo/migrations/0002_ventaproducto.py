# Generated by Django 5.1.6 on 2025-02-13 03:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VentaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogo.productos')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='catalogo.ventas')),
            ],
        ),
    ]
