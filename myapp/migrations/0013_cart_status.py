# Generated by Django 3.0 on 2021-01-05 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(default='pending', max_length=100),
        ),
    ]
