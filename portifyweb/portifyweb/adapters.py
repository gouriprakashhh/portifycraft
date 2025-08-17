# yourapp/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from portifyweb.utils import generate_unique_username

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        if not user.username:
            # If no username is set, generate a unique username
            user.username = generate_unique_username(user)
            user.save()  # Ensure the user object is saved with the new username
        
        return user
