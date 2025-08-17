from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),

    # Google Sign-in entry point (can be reused for login or signup triggers)
    path('google/signin/', views.google_signin, name='google_signin'),
    path('google/login/', views.google_login, name='google_login'),

    # Separate callbacks for login and signup
    path('google/accounts/google/callback-login/', views.google_callback_login, name='google_callback_login'),
    path('google/accounts/google/callback-signup/', views.google_callback_signup, name='google_callback_signup'),

    # Error page
    path('google/login-error/', views.login_error, name='login_error'),
]
