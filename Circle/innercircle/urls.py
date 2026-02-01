from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.item_list_view, name='item_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Items
    path('items/create/', views.item_create_view, name='item_create'),
    path('items/<int:item_id>/', views.item_detail_view, name='item_detail'),
    path('items/<int:item_id>/edit/', views.item_update_view, name='item_update'),
    path('items/<int:item_id>/delete/', views.item_delete_view, name='item_delete'),
    path('my-items/', views.my_items_view, name='my_items'),
    
    # Friends
    path('friends/search/', views.friend_search_view, name='friend_search'),
    path('friends/request/<int:user_id>/', views.friend_request_create_view, name='friend_request_create'),
    path('friends/requests/', views.friend_requests_view, name='friend_requests'),
    path('friends/requests/<int:request_id>/accept/', views.friend_request_accept_view, name='friend_request_accept'),
    path('friends/requests/<int:request_id>/decline/', views.friend_request_decline_view, name='friend_request_decline'),
    
    # Swap Requests
    path('requests/create/<int:item_id>/', views.request_create_view, name='request_create'),
    path('requests/', views.request_list_view, name='request_list'),
    path('requests/<int:request_id>/accept/', views.request_accept_view, name='request_accept'),
    path('requests/<int:request_id>/cancel/', views.request_cancel_view, name='request_cancel'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='friend_profile'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notif_id>/read/', views.notification_read_view, name='notification_read'),
]

