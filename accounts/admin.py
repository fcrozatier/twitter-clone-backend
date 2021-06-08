from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from graphql_auth.models import UserStatus

from accounts.forms import CreateUserForm
from accounts.models import User

admin.site.register(UserStatus)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "verified", "uid", "is_staff")
    list_filter = ("is_staff", "is_active", "status__verified")
    search_fields = ("username", "email")
    ordering = ("username",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    add_form = CreateUserForm
    filter_horizontal = ()

    @admin.display(boolean=True)
    def verified(self, user):
        return user.status.verified
