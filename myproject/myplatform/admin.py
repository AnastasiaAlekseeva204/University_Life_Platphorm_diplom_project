from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Community
from .models import Event
from .models import Faculty
from django.utils.html import mark_safe
from mptt.admin import DraggableMPTTAdmin
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username','last_name','email','is_staff','is_active','role','image_preview','faculty','name','last_name_student','middle_name_student','about_text','birth_date']
    list_filter = ['is_staff','is_active','role','faculty']
    fieldsets = UserAdmin.fieldsets+(
        ('Custom Fields', {
            'fields': ('role','img','name','last_name_student','middle_name_student','birth_date','faculty','about_text')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets+(
        ('Custom Fields', {
            'fields':('role','img','name','last_name_student','middle_name_student','birth_date','faculty','about_text')
        }),
    )
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Для существующих пользователей разрешаем изменение роли
        if obj:
            form.base_fields['role'].disabled = False
        return form
    def image_preview(self, obj):
        if obj.img:
            return mark_safe(f'<img src="{obj.img.url}" width="50" height="50" />')
        return "Нет изображения"
    
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name','description','organizator','img','status','created_at','image_preview']
    list_filter = ['status','created_at']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.img:
            return mark_safe(f'<img src="{obj.img.url}" width="50" height="50" />')
        return "Нет изображения"
    image_preview.short_description = 'Превью'

class EventAdmin(admin.ModelAdmin):
    list_display = ['name','date_time','location','organizator','max_participants','img','created_at','image_preview']
    list_filter = ['created_at']
    readonly_fields = ['image_preview']
    def image_preview(self, obj):
        if obj.img:
            return mark_safe(f'<img src="{obj.img.url}" width="50" height="50" />')
        return "Нет изображения"
    
class FacultyAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title',
                    'description', 'created_at', 'updated_at','image_preview')
    list_display_links = ('indented_title',)
    readonly_fields = ['image_preview']
    def image_preview(self, obj):
        if obj.img:
            return mark_safe(f'<img src="{obj.img.url}" width="50" height="50" />')
        return "Нет изображения"

admin.site.register(User, CustomUserAdmin)
admin.site.register(Community,CommunityAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Faculty, FacultyAdmin)

