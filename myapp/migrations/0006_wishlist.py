# Generated by Django 3.0 on 2020-12-26 10:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_user_user_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.User')),
            ],
        ),
    ]