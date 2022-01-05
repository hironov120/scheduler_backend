from django.contrib import admin

from .models import User, Task, TaskProcessed, Note, NoteProcessed


@admin.register(User, Task, TaskProcessed, Note, NoteProcessed)
class UserAdmin(admin.ModelAdmin):
    pass

