from django.contrib import admin
from .models import Worker, Attendance, UserProfile

admin.site.register(Worker)
admin.site.register(Attendance)
admin.site.register(UserProfile)
