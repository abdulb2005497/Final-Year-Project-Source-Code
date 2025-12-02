from django.urls import path
from . import views

urlpatterns = [
    
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),

    
    path(
        "forgot-password-email/",
        views.forgot_password_email_view,
        name="forgot_password_email",
    ),

    
    path("magic-word/", views.magic_word_check, name="magic_word_check"),

    path("dashboard/", views.dashboard_router, name="dashboard_router"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/plumber/", views.plumber_dashboard, name="plumber_dashboard"),
    path("dashboard/customer/", views.customer_dashboard, name="customer_dashboard"),
]
