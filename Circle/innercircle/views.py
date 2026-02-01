from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import Http404
from django.views.generic import FormView

from .forms import RegisterForm, ItemForm, ProfileForm, SwapRequestForm
from .models import Item, FriendRequest, SwapRequest, Notification, Profile

User = get_user_model()


def login_view(request):
    """User login with form validation"""
    if request.user.is_authenticated:
        return redirect('item_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('item_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'innercircle/login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, "You've been logged out.")
    return redirect('login')


def register_view(request):
    """New user registration"""
    if request.user.is_authenticated:
        return redirect('item_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for new user
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('item_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'innercircle/register.html', {'form': form})


@login_required
def item_list_view(request):
    """Main feed showing items from friends"""
    # Get friend IDs
    friend_ids = FriendRequest.objects.filter(
        Q(from_user=request.user, accepted=True) | Q(to_user=request.user, accepted=True)
    ).values_list('from_user', 'to_user')
    
    friend_set = set()
    for from_id, to_id in friend_ids:
        friend_set.add(from_id)
        friend_set.add(to_id)
    friend_set.discard(request.user.id)
    
    # Include own items + friends' items
    items = Item.objects.filter(
        Q(owner=request.user) | Q(owner_id__in=friend_set),
        is_available=True
    ).select_related('owner').prefetch_related('swap_requests').order_by('-created_at')
    
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'innercircle/item_list.html', {'page_obj': page_obj})


@login_required
def item_create_view(request):
    """Create new item"""
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            messages.success(request, 'Item posted successfully!')
            return redirect('item_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ItemForm()
    return render(request, 'innercircle/item_form.html', {'form': form, 'title': 'Post New Item'})


@login_required
def item_detail_view(request, item_id):
    """View single item details"""
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'innercircle/item_detail.html', {'item': item})


@login_required
def item_update_view(request, item_id):
    """Edit item (owner only)"""
    item = get_object_or_404(Item, pk=item_id)
    if item.owner != request.user:
        messages.error(request, "You can only edit your own items.")
        return redirect('item_list')
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated!')
            return redirect('item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'innercircle/item_form.html', {'form': form, 'title': 'Edit Item'})


@login_required
def item_delete_view(request, item_id):
    """Delete item (owner only)"""
    item = get_object_or_404(Item, pk=item_id)
    if item.owner != request.user:
        messages.error(request, "You can only delete your own items.")
        return redirect('item_list')
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted.')
        return redirect('my_items')
    return render(request, 'innercircle/item_delete_confirm.html', {'item': item})


@login_required
def my_items_view(request):
    """View user's own items"""
    items = Item.objects.filter(owner=request.user).order_by('-created_at')
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'innercircle/my_items.html', {'page_obj': page_obj})


@login_required
def friend_search_view(request):
    """Search for users to send friend requests"""
    query = request.GET.get('q', '').strip()
    results = []
    if query and len(query) >= 2:
        results = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(pk=request.user.pk)[:20]
    return render(request, 'innercircle/friend_search.html', {'results': results, 'query': query})


@login_required
def friend_requests_view(request):
    """View incoming and outgoing friend requests"""
    incoming = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    outgoing = FriendRequest.objects.filter(from_user=request.user, accepted=False)
    accepted = FriendRequest.objects.filter(
        Q(from_user=request.user, accepted=True) | Q(to_user=request.user, accepted=True)
    )
    
    return render(request, 'innercircle/friend_requests.html', {
        'incoming': incoming,
        'outgoing': outgoing,
        'accepted': accepted
    })


@login_required
def friend_request_create_view(request, user_id):
    """Send friend request to a user"""
    to_user = get_object_or_404(User, pk=user_id)
    
    if to_user == request.user:
        messages.error(request, "You can't send a request to yourself.")
        return redirect('friend_search')
    
    # Check if request already exists
    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        messages.warning(request, f"You already sent a request to {to_user.username}.")
        return redirect('friend_search')
    
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    Notification.objects.create(
        user=to_user,
        text=f"{request.user.username} sent you a friend request",
        notification_type='friend_request'
    )
    messages.success(request, f"Friend request sent to {to_user.username}!")
    return redirect('friend_search')


@login_required
def friend_request_accept_view(request, request_id):
    """Accept friend request"""
    fr = get_object_or_404(FriendRequest, pk=request_id)
    if fr.to_user != request.user:
        messages.error(request, "Invalid request.")
        return redirect('friend_requests')
    
    fr.accept()
    messages.success(request, f"You and {fr.from_user.username} are now friends!")
    return redirect('friend_requests')


@login_required
def friend_request_decline_view(request, request_id):
    """Decline friend request"""
    fr = get_object_or_404(FriendRequest, pk=request_id)
    if fr.to_user != request.user:
        messages.error(request, "Invalid request.")
        return redirect('friend_requests')
    
    fr.delete()
    messages.success(request, "Friend request declined.")
    return redirect('friend_requests')


@login_required
def request_create_view(request, item_id):
    """Create swap/purchase request for an item"""
    item = get_object_or_404(Item, pk=item_id)
    
    if item.owner == request.user:
        messages.error(request, "You can't request your own items.")
        return redirect('item_list')
    
    # Check friendship
    is_friend = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=item.owner, accepted=True) |
        Q(from_user=item.owner, to_user=request.user, accepted=True)
    ).exists()
    
    if not is_friend:
        messages.error(request, "You must be friends to request items.")
        return redirect('item_detail', item_id=item.id)
    
    if request.method == 'POST':
        form = SwapRequestForm(request.POST)
        if form.is_valid():
            SwapRequest.objects.create(
                sender=request.user,
                receiver=item.owner,
                item=item,
                message=form.cleaned_data.get('message', '')
            )
            Notification.objects.create(
                user=item.owner,
                text=f"{request.user.username} requested {item.title}",
                notification_type='swap_request'
            )
            messages.success(request, 'Swap request sent!')
            return redirect('request_list')
    else:
        form = SwapRequestForm()
    return render(request, 'innercircle/request_form.html', {'form': form, 'item': item})


@login_required
def request_list_view(request):
    """View incoming and outgoing swap requests"""
    incoming = SwapRequest.objects.filter(receiver=request.user).select_related('sender', 'item')
    outgoing = SwapRequest.objects.filter(sender=request.user).select_related('receiver', 'item')
    
    paginator_in = Paginator(incoming, 10)
    paginator_out = Paginator(outgoing, 10)
    
    page_in = paginator_in.get_page(request.GET.get('page_in'))
    page_out = paginator_out.get_page(request.GET.get('page_out'))
    
    return render(request, 'innercircle/request_list.html', {
        'incoming': page_in,
        'outgoing': page_out
    })


@login_required
def request_accept_view(request, request_id):
    """Accept swap request"""
    sr = get_object_or_404(SwapRequest, pk=request_id)
    if sr.receiver != request.user:
        messages.error(request, "Invalid request.")
        return redirect('request_list')
    
    sr.accept()
    messages.success(request, "Swap request accepted!")
    return redirect('request_list')


@login_required
def request_cancel_view(request, request_id):
    """Cancel/decline swap request"""
    sr = get_object_or_404(SwapRequest, pk=request_id)
    if sr.receiver != request.user and sr.sender != request.user:
        messages.error(request, "Invalid request.")
        return redirect('request_list')
    
    sr.cancel()
    messages.success(request, "Request cancelled.")
    return redirect('request_list')


@login_required
def profile_view(request, username=None):
    """View user profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile = get_object_or_404(Profile, user=user)
    items = user.items.filter(is_available=True)
    
    return render(request, 'innercircle/profile.html', {
        'profile_user': user,
        'profile': profile,
        'items': items
    })


@login_required
def profile_edit_view(request):
    """Edit own profile"""
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Update user fields if provided
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'innercircle/profile_edit.html', {'form': form})


@login_required
def notifications_view(request):
    """View user notifications"""
    notifications = request.user.notifications.all()
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'innercircle/notifications.html', {'page_obj': page_obj})


@login_required
def notification_read_view(request, notif_id):
    """Mark notification as read"""
    notif = get_object_or_404(Notification, pk=notif_id)
    if notif.user != request.user:
        messages.error(request, "Invalid notification.")
        return redirect('notifications')
    
    notif.mark_as_read()
    messages.success(request, "Notification marked as read.")
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))

