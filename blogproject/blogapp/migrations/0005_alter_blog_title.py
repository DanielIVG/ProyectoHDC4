# Generated by Django 5.1.3 on 2025-04-24 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogapp", "0004_blog_contenido_blog_imagen"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="title",
            field=models.CharField(max_length=255),
        ),
    ]
