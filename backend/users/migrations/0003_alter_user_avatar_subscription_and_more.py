# Generated by Django 4.2.16 on 2024-11-16 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_subscription_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, default='', upload_to='users/avatars/', verbose_name='Аватар'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'db_table': 'users_subscription',
                'unique_together': {('user', 'author')},
            },
        ),
        migrations.AddField(
            model_name='user',
            name='subscription_authors',
            field=models.ManyToManyField(blank=True, related_name='subscription_users', through='users.Subscription', to=settings.AUTH_USER_MODEL, verbose_name='Подписан на авторов'),
        ),
    ]