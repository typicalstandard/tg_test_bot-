from asgiref.sync import async_to_sync
from django.contrib import admin
from .models import Client, Broadcast
from aiogram import Bot
import os

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'telegram_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'telegram_id')




@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'created_at', 'sent')
    actions = ['send_broadcast_action']

    def send_broadcast_action(self, request, queryset):
        for broadcast in queryset.filter(sent=False):
            try:
                broadcast.sent = True
                broadcast.save()
                self.message_user(request, f"Рассылка '{broadcast.subject}' успешно отправлена.")
            except Exception as e:
                self.message_user(request, f"Ошибка при отправке рассылки: {e}", level='error')

    send_broadcast_action.short_description = "Отправить выбранные рассылки"



