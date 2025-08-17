# views.py
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .decorators import custom_login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import CustomUser,GoogleUser
from django.utils import timezone
from django.contrib.auth import logout as django_logout
from google.auth.transport.requests import Request # type: ignore
from google.oauth2 import id_token # type: ignore
from google_auth_oauthlib.flow import Flow # type: ignore
from django.conf import settings
import os




from django.contrib import messages


from django.utils.timezone import now

def signup_view(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if the email already exists in either user model
        if CustomUser.objects.filter(email=email).exists() or GoogleUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('signup')  # ✅ Redirect to clear error message

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')  # ✅ Redirect to clear error message

        # Create user
        hashed_password = make_password(password)
        user = CustomUser.objects.create(
            name=name,
            email=email,
            password=hashed_password,
            is_active=True,
            last_login=now()
        )

        request.session['user_id'] = user.id
        request.session.set_expiry(3600)

        messages.success(request, "Account created successfully!")
        return redirect('home')

    return render(request, 'auth/signup.html')


def login_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            CustomUser.objects.get(id=user_id)
            return redirect('home')
        except CustomUser.DoesNotExist:
            del request.session['user_id']

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                if user.is_active:
                    user.last_login = timezone.now()
                    user.save()
                    request.session['user_id'] = user.id
                    request.session.set_expiry(3600)
                    return redirect('home')
                else:
                    messages.error(request, "Account is inactive. Please contact support.")
            else:
                messages.error(request, "Invalid password.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Email or Password is wrong")

        # 👇 Redirect to clear the message after display
        return redirect('login')  # PRG Pattern

    return render(request, 'auth/login.html')




def logout_view(request):
    # Log out from Django's auth system (this clears the session data)
    django_logout(request)

    # Remove custom session-based login
    request.session.pop('user_id', None)

    return redirect('home')  # Redirect after logout

import uuid
import random
from django.utils import timezone
from .models import GuestSession, GoogleUser, CustomUser

def get_client_ip(request):
    """Utility function to get the client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
import time
def generate_readable_name():
    """Generate a simple readable name like 'Guest_001'."""
    timestamp = int(time.time())  # Get the current timestamp
    random_number = random.randint(100, 999)  # Random number between 100 and 999

    # Ensure the name is unique by checking if it already exists in the database
    name = f"Guest_{timestamp}_{random_number}"

    # Check if name already exists and regenerate if necessary
    while GuestSession.objects.filter(name=name).exists():
        random_number = random.randint(100, 999)  # Generate a new random number
        name = f"Guest_{timestamp}_{random_number}"

    return name
def home_view(request):
    user = None
    user_id = request.session.get('user_id')  # Retrieve custom user ID from session

    if user_id:
        try:
            # Try fetching from GoogleUser first
            user = GoogleUser.objects.get(id=user_id)
        except GoogleUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user = None  # Invalid ID or user deleted

    # Delete guest sessions older than 1 minute (for testing)
    cutoff = timezone.now() - timedelta(days=10)
    GuestSession.objects.filter(last_active__lt=cutoff).delete()


    # Handle guest session if no authenticated user
    if not user:
        guest_token = request.session.get('guest_token')
        if not guest_token:
            # Generate and save a new guest session
            guest_token = uuid.uuid4().hex
            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            readable_name = generate_readable_name()  # Generate simple readable name

            GuestSession.objects.create(
                token=guest_token,
                last_active=timezone.now(),
                ip_address=ip,
                user_agent=user_agent,
                name=readable_name  # Store simple readable name
            )

            # Store token in session
            request.session['guest_token'] = guest_token
        else:
            # Update last active time if guest session already exists
            GuestSession.objects.filter(token=guest_token).update(last_active=timezone.now())

    return render(request, 'main/home.html', {'user': user})



def signup_or_login_view(request):
    # You can show a simple template asking the user to choose sign up or log in
    return render(request, 'auth/signup_or_login.html')



GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def google_signin(request):
    # Define redirect URI for signup flow
    REDIRECT_URI = "https://fed8-45-249-169-180.ngrok-free.app/google/accounts/google/callback-signup/"
    client_secrets_file = os.path.join(settings.BASE_DIR, 'authentication', 'client_secret.json')

    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=GOOGLE_SCOPES
    )
    flow.redirect_uri = REDIRECT_URI

    # Generate authorization URL with new state for signup
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['signup_state'] = state  # Save the state for signup flow

    return redirect(authorization_url)

from google.oauth2 import id_token
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
import os
import traceback

def google_callback_signup(request):
    REDIRECT_URI = "https://fed8-45-249-169-180.ngrok-free.app/google/accounts/google/callback-signup/"
    state = request.session.get('signup_state')

    if not state:
        print("❌ No state found in session.")
        return redirect('/google/login-error/')

    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'authentication', 'client_secret.json'),
        scopes=GOOGLE_SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URI

    try:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        print("✅ Token fetched.")
    except Exception as e:
        print("❌ Token fetch failed:", e)
        traceback.print_exc()
        request.session.pop('signup_state', None)
        return redirect('/google/login-error/')

    try:
        # Verify ID token with 5 sec clock skew tolerance
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=5
        )
        print("✅ ID token verified.")
    except ValueError as e:
        print("❌ ID token verification failed:", e)
        traceback.print_exc()
        request.session.pop('signup_state', None)
        return redirect('/google/login-error/')

    email = id_info.get("email")
    name = id_info.get("name") or email.split("@")[0]
    google_id_value = id_info.get("sub")
    profile_picture = id_info.get("picture")

    if not email:
        print("❌ Email not found in Google response.")
        request.session.pop('signup_state', None)
        messages.error(request, "Google account does not provide an email address.")
        return redirect('/google/login-error/')

    # Check if email exists
    if CustomUser.objects.filter(email=email).exists() or GoogleUser.objects.filter(email=email).exists():
        print("❌ Email already exists. Redirecting to login.")
        messages.info(request, "This email is already registered. Please log in.")
        request.session.pop('signup_state', None)
        return redirect('/login/')

    # Save new GoogleUser
    google_user = GoogleUser.objects.create(
        email=email,
        name=name,
        google_id=google_id_value,
        profile_picture=profile_picture,
        created_at=timezone.now(),
        last_login=timezone.now(),
        is_active=True
    )

    request.session['user_id'] = google_user.id
    print("✅ New user saved and logged in.")
    request.session.pop('signup_state', None)
    return redirect('home')


def login_error(request):
    return HttpResponse("❌ Google login failed or your email is not registered. Please try again or sign up.")


def google_login(request):
    # Define redirect URI for login flow
    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'authentication', 'client_secret.json'),
        scopes=GOOGLE_SCOPES
    )
    flow.redirect_uri = "https://fed8-45-249-169-180.ngrok-free.app/google/accounts/google/callback-login/"

    # Generate authorization URL with new state for login
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['login_state'] = state  # Save the state for login flow

    return redirect(authorization_url)

def google_callback_login(request):
    REDIRECT_URI = "https://fed8-45-249-169-180.ngrok-free.app/google/accounts/google/callback-login/"
    state = request.session.get('login_state')

    if not state:
        print("❌ No state found in session.")
        return redirect('/google/login-error/')

    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'authentication', 'client_secret.json'),
        scopes=GOOGLE_SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URI

    try:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        print("✅ Token fetched.")
    except Exception as e:
        print("❌ Token fetch failed:", e)
        traceback.print_exc()
        request.session.pop('login_state', None)
        return redirect('/google/login-error/')

    try:
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=5  # Allow small clock mismatch
        )
        print("✅ ID token verified.")
    except ValueError as e:
        print("❌ ID token verification failed:", e)
        traceback.print_exc()
        request.session.pop('login_state', None)
        return redirect('/google/login-error/')

    email = id_info.get("email")
    if not email:
        print("❌ Email not provided by Google.")
        messages.error(request, "Google account did not provide an email address.")
        request.session.pop('login_state', None)
        return redirect('/google/login-error/')

    # Try to authenticate from GoogleUser or CustomUser
    user = None
    try:
        user = GoogleUser.objects.get(email=email)
        print("✅ GoogleUser found.")
    except GoogleUser.DoesNotExist:
        try:
            user = CustomUser.objects.get(email=email)
            print("✅ CustomUser found.")
        except CustomUser.DoesNotExist:
            print("❌ Email not registered in either model.")
            messages.error(request, "No account found with this email. Please sign up.")
            request.session.pop('login_state', None)
            return redirect('signup')

    # Update last_login and save
    user.last_login = timezone.now()
    user.save()

    # Set session with expiry
    request.session['user_id'] = user.id
    print("✅ User session set with 1-hour expiry.")

    # Always clean up session state
    request.session.pop('login_state', None)
    print("✅ User logged in and session state cleared.")
    return redirect('home')
