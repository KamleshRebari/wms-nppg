from django.db import models

class Worker(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(upload_to="worker_photos/", blank=True, null=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    SLOT_CHOICES = (
        (1, "Slot 1 (9-10)"),
        (2, "Slot 2 (1-2)"),
        (3, "Slot 3 (4-5)"),
    )

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    slot = models.IntegerField(choices=SLOT_CHOICES)
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ("worker", "date", "slot")  # no duplicate
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    dob = models.DateField()
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def __str__(self):
        return self.user.username
class Slot(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
