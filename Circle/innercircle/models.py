from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture (PNG/JPG)")
    bio = models.TextField(blank=True, max_length=500, help_text="Brief bio (max 500 chars)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_friends_count(self):
        """Count confirmed friendships"""
        return FriendRequest.objects.filter(
            models.Q(from_user=self.user, accepted=True) | models.Q(to_user=self.user, accepted=True)
        ).count()

    def get_items_count(self):
        """Count items posted"""
        return self.user.items.count()


class Item(models.Model):
    CATEGORY_CHOICES = [
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('dresses', 'Dresses'),
        ('outerwear', 'Outerwear'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    SIZE_CHOICES = [
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
    ]
    CONDITION_CHOICES = [
        ('new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='items/%Y/%m/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    is_available = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['category', 'is_available']),
        ]
        verbose_name_plural = "Items"

    def __str__(self):
        return f"{self.title} ({self.get_condition_display()}) - {self.owner.username}"

    def clean(self):
        if len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters long.")


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False, db_index=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to_user', 'accepted']),
        ]

    def __str__(self):
        status = "✓ Accepted" if self.accepted else "✗ Pending"
        return f"{self.from_user} → {self.to_user} [{status}]"

    def accept(self):
        """Accept friend request and create reciprocal friendship"""
        self.accepted = True
        self.accepted_at = timezone.now()
        self.save()
        # Create notification for sender
        Notification.objects.create(
            user=self.to_user,
            text=f"{self.from_user.username} accepted your friend request",
            notification_type='request_accepted'
        )


class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_swap_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_swap_requests')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='swap_requests')
    message = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['sender', 'status']),
        ]

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} | {self.item.title} [{self.get_status_display()}]"

    def accept(self):
        """Accept swap request"""
        self.status = 'accepted'
        self.save()
        Notification.objects.create(
            user=self.sender,
            text=f"{self.receiver.username} accepted your swap request for {self.item.title}",
            notification_type='swap_accepted'
        )

    def complete(self):
        """Mark swap as completed"""
        self.status = 'completed'
        self.item.is_available = False
        self.item.save()
        self.save()

    def cancel(self):
        """Cancel swap request"""
        self.status = 'cancelled'
        self.save()


class Notification(models.Model):
    TYPES = [
        ('friend_request', 'Friend Request'),
        ('request_accepted', 'Request Accepted'),
        ('swap_request', 'Swap Request'),
        ('swap_accepted', 'Swap Accepted'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPES, default='swap_request')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read', '-created_at']),
        ]

    def __str__(self):
        status = "📖 Read" if self.read else "📧 Unread"
        return f"{self.user.username}: {self.text} [{status}]"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()
