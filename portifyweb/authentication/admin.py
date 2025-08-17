from django.contrib import admin
from .models import CustomUser,GoogleUser,GuestSession
# Register your models here


admin.site.register(CustomUser)
admin.site.register(GoogleUser)
class GuestSessionAdmin(admin.ModelAdmin):
    list_display = ('name','last_active', 'ip_address')

admin.site.register(GuestSession, GuestSessionAdmin)