from django.contrib import admin
from .models import File, Track
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import User

admin.site.site_header = "Misojo Admin"
admin.site.site_title = 'Misojo'
admin.site.site_url = '/'
admin.site.index_title = "Admin"


# Data models
@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'path', 'current_page', 'uploaded_at', 'last_modified')
    list_filter = ('user', 'uploaded_at', 'last_modified')
    search_fields = ('user', 'path', 'uploaded_at', 'last_modified')


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'path', 'page')
    list_filter = ('file__name', 'file__user')
    search_fields = ('file', 'path', 'page')


# Custom user model setup
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active", "is_admin"]

    def clean_password2(self):
        """ Password match validation when creating a new user """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """ Save the provided password in hashed format """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_admin"
        ]


class UserAdmin(BaseUserAdmin):
    # forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # fields to be used in displaying the User model.
    list_display = ["email", "first_name", "last_name", "is_admin", "is_active"]
    list_filter = ["is_admin", "is_active"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name"]}),
        ("Permissions", {"fields": ["is_admin", "is_active"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


# register the new UserAdmin
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)