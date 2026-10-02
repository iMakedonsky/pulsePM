from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from organizations.models import Member

from .models import User


class MemberInline(admin.TabularInline[Member, User]):
    model = Member
    extra = 0
    fields = (
        'organization',
        'role',
        'position',
    )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):  # type: ignore[type-arg]
    ordering = ('email',)
    list_display = ('email', 'id', 'first_name', 'last_name', 'is_staff', 'is_active')
    readonly_fields = ('id',)  # why isn't it visible?
    search_fields = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [
        MemberInline,
    ]
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),)
