from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        username = "Ashok"
        password = "Ashoknppg@123"

        user, created = User.objects.get_or_create(username=username)

        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        print("✅ Admin reset successful!")
        print("Username:", username)
        print("Password:", password)
