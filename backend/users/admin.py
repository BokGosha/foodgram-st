from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username',
        'email',
        'is_staff',
    )
    search_fields = (
        'email',
        'username',
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
