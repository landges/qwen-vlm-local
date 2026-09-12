import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the initial administrator if it does not exist"

    def handle(self, *args, **options):
        username = os.environ.get("MEMORY_ADMIN_USERNAME")
        password = os.environ.get("MEMORY_ADMIN_PASSWORD")
        email = os.environ.get("MEMORY_ADMIN_EMAIL", "")
        if not username or not password:
            self.stdout.write("Initial administrator is not configured")
            return
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created administrator {username}"))

