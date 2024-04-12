# Generated by Django 4.2.11 on 2024-04-12 21:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0004_remove_paper_reviews_last_updated_paper_index_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID'),
        ),
    ]
