from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class MyUserAdmin(UserAdmin):
    # Указываем, какие поля выводить в списке пользователей
    # Убираем first_name и last_name, так как их нет в модели User
    list_display = ('email', 'username', 'is_staff', 'is_active')

    # Указываем, по каким полям можно фильтровать
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    # Поля, которые будут видны при редактировании пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('username', 'phone_number')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_deleted')}),
        ('Важные даты', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at')

    # Поиск по email и нику
    search_fields = ('email', 'username')
    ordering = ('email',)

# Регистрируем модель User с нашей новой админкой
admin.site.register(User, MyUserAdmin)

# Также зарегистрируем профиль, чтобы его было видно отдельно
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'points')
    search_fields = ('user__username', 'first_name', 'last_name')