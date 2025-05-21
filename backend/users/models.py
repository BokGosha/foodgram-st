from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message='Логин может содержать только буквы, цифры и @/./+/-/_'
    )

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[username_validator],
    )

    email = models.EmailField('Адрес email', unique=True)

    first_name = models.CharField('Имя', max_length=150)

    last_name = models.CharField('Фамилия', max_length=150)

    password = models.CharField('Пароль', max_length=150)

    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь',
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='followed',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user']

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
