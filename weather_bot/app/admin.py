from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ({name}, {telegram_id}, {lat}, {lon})

admin.site.register(User, UserAdmin)