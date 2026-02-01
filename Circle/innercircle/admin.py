from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Item, FriendRequest, SwapRequest, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'items_count', 'friends_count', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def items_count(self, obj):
        return obj.get_items_count()
    items_count.short_description = "Items"

    def friends_count(self, obj):
        return obj.get_friends_count()
    friends_count.short_description = "Friends"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'condition', 'availability_badge', 'created_at')
    list_filter = ('category', 'condition', 'is_available', 'created_at')
    search_fields = ('title', 'owner__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Ownership', {'fields': ('owner',)}),
        ('Content', {'fields': ('title', 'description', 'photo')}),
        ('Details', {'fields': ('category', 'size', 'condition', 'is_available')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def availability_badge(self, obj):
        color = '90EE90' if obj.is_available else 'FFB6C6'
        status = 'Available' if obj.is_available else 'Unavailable'
        return format_html(f'<span style="background-color: #{color}; padding: 5px 10px; border-radius: 3px;">{status}</span>')
    availability_badge.short_description = "Status"


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status_badge', 'created_at')
    list_filter = ('accepted', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created_at', 'accepted_at')

    def status_badge(self, obj):
        color = '90EE90' if obj.accepted else 'FFD700'
        status = 'Accepted' if obj.accepted else 'Pending'
        return format_html(f'<span style="background-color: #{color}; padding: 5px 10px; border-radius: 3px;">{status}</span>')
    status_badge.short_description = "Status"


@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'item', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'item__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Users', {'fields': ('sender', 'receiver')}),
        ('Item', {'fields': ('item',)}),
        ('Message', {'fields': ('message',)}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def status_badge(self, obj):
        colors = {
            'pending': 'FFD700',
            'accepted': '90EE90',
            'completed': '87CEEB',
            'cancelled': 'FFB6C6',
        }
        color = colors.get(obj.status, 'CCCCCC')
        return format_html(f'<span style="background-color: #{color}; padding: 5px 10px; border-radius: 3px;">{obj.get_status_display()}</span>')
    status_badge.short_description = "Status"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'notification_type', 'read_badge', 'created_at')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('user__username', 'text')
    readonly_fields = ('created_at', 'read_at')

    def read_badge(self, obj):
        color = '90EE90' if obj.read else 'FFD700'
        status = 'Read' if obj.read else 'Unread'
        return format_html(f'<span style="background-color: #{color}; padding: 5px 10px; border-radius: 3px;">{status}</span>')
    read_badge.short_description = "Read Status"

