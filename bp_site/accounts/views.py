from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Profile
from django.shortcuts import render

def user_in_group(user, group_name: str) -> bool:
    return user.groups.filter(name=group_name).exists()

def login_view(request):
    if request.method == "POST":
        login_identifier = request.POST.get("username")
        password = request.POST.get("password")

        username = login_identifier

        try:
            if User.objects.filter(email__iexact=login_identifier).exists():
                user_obj = User.objects.get(email__iexact=login_identifier)
                username = user_obj.username
        except User.DoesNotExist:
            username = login_identifier

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "accounts/login.html", {
                "error": "Invalid login details"
            })

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("/")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "accounts/register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {
                "error": "Username is already taken"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "accounts/register.html", {
                "error": "An account with this email already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        try:
            customer_group = Group.objects.get(name="Customer")
            user.groups.add(customer_group)
        except Group.DoesNotExist:

            pass

        login(request, user)
        return redirect("/")

    return render(request, "accounts/register.html")


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        magic_word = request.POST.get("magic_word", "").strip()

        if magic_word:
            profile.magic_word = magic_word
            profile.save()

        return redirect("/accounts/profile/")

    return render(request, "accounts/profile.html")


def forgot_password_email_view(request):

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            return render(request, "accounts/forgot_password_email.html", {
                "error": "Please enter your email address."
            })

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "accounts/forgot_password_email.html", {
                "error": "If this email is linked to an account, you'll be able to continue."
            })

        request.session["reset_email"] = user.email

        return redirect("/accounts/magic-word/")

    return render(request, "accounts/forgot_password_email.html")



def magic_word_check(request):
    reset_email = request.session.get("reset_email")

    if not reset_email:
        return redirect("/accounts/forgot-password-email/")

    if request.method == "POST":
        magic = request.POST.get("magic_word", "").strip()
        new_password1 = request.POST.get("new_password1", "")
        new_password2 = request.POST.get("new_password2", "")

        if not magic:
            return render(request, "accounts/magic_word_check.html", {
                "email": reset_email,
                "error": "Please enter your magic word."
            })

        try:
            user = User.objects.get(email=reset_email)
            profile = Profile.objects.get(user=user)
        except (User.DoesNotExist, Profile.DoesNotExist):
            return render(request, "accounts/magic_word_check.html", {
                "email": reset_email,
                "error": "We couldn't find an account for this email. Please start again."
            })

        if profile.magic_word != magic:
            return render(request, "accounts/magic_word_check.html", {
                "email": reset_email,
                "error": "Magic word is incorrect."
            })

        if not new_password1 or not new_password2:
            return render(request, "accounts/magic_word_check.html", {
                "email": reset_email,
                "error": "Please enter your new password twice."
            })

        if new_password1 != new_password2:
            return render(request, "accounts/magic_word_check.html", {
                "email": reset_email,
                "error": "Passwords do not match."
            })

        user.set_password(new_password1)
        user.save()

        request.session.pop("reset_email", None)

        return redirect("/accounts/login/")

    return render(request, "accounts/magic_word_check.html", {
        "email": reset_email
    })



@login_required
def dashboard_router(request):
    user = request.user

    if user.is_superuser or user_in_group(user, "Admin"):
        return redirect("admin_dashboard")

    if user_in_group(user, "Plumber"):
        return redirect("plumber_dashboard")

    if user_in_group(user, "Customer"):
        return redirect("customer_dashboard")

    return redirect("customer_dashboard")


@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or user_in_group(request.user, "Admin")):
        return redirect("dashboard_router")

    return render(request, "accounts/admin_dashboard.html")


@login_required
def plumber_dashboard(request):
    if not (user_in_group(request.user, "Plumber") or request.user.is_superuser):
        return redirect("dashboard_router")

    return render(request, "accounts/plumber_dashboard.html")


@login_required
def customer_dashboard(request):
    if not (user_in_group(request.user, "Customer") or request.user.is_superuser):
        return redirect("dashboard_router")

    return render(request, "accounts/customer_dashboard.html")
