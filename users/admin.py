from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'is_staff',
        'commentaries'
    )

    def commentaries(self, obj):
        return obj.commentaries.count()

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
