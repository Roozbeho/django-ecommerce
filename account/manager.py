from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomCustomerManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError(_("Users must have an email address"))
        if not username:
            raise ValueError(_("Users must have an username"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superusers must have superuser=True"))
        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True"))
        if not extra_fields.get("is_active"):
            raise ValueError(_("Superuser must have is_active=True"))

        return self.create_user(email, username, password, **extra_fields)
