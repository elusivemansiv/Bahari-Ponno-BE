from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile

admin.site.register(User, UserAdmin)
admin.site.register(CustomerProfile)
