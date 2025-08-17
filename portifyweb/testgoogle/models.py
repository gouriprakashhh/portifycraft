import uuid
from django.db import models
from authentication.models import GuestSession
import json



class PersonalDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    guest_session = models.OneToOneField(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    short_bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.full_name or str(self.id)
    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class ContactInfo(models.Model):
     
    guest_session = models.OneToOneField(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class DesignPreferences(models.Model):
     
    guest_session = models.OneToOneField(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    primary_color = models.CharField(max_length=7, null=True, blank=True)
    secondary_color = models.CharField(max_length=7, null=True, blank=True)
    design_style = models.CharField(max_length=100, null=True, blank=True)
    animation_style = models.CharField(max_length=100, null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class DevicePreferences(models.Model):
     
    guest_session = models.OneToOneField(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    devices = models.JSONField(null=True, blank=True)
    hamburger_menu = models.BooleanField(default=False, null=True, blank=True)
    menu_items = models.JSONField(null=True, blank=True)
    navbar = models.BooleanField(default=False, null=True, blank=True)
    navbar_items = models.JSONField(null=True, blank=True)
    footer_social = models.BooleanField(default=False, null=True, blank=True)
    footer_contact = models.BooleanField(default=False, null=True, blank=True)
    footer_enabled = models.BooleanField(default=False, null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


import json

class Skill(models.Model):
    guest_session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    skills = models.TextField(default='[]')  # Store skills as JSON string

    def get_skills(self):
        # Converts the JSON string back into a list, with error handling
        try:
            return json.loads(self.skills) if self.skills else []
        except json.JSONDecodeError:
            return []  # Return an empty list if decoding fails

    def set_skills(self, skills_list):
        # Converts the list into a JSON string for storage
        self.skills = json.dumps(skills_list)
    
    def __str__(self):
        # Show a readable representation of the skills in the object
        skills = self.get_skills()
        return ', '.join(skills) if skills else "No skills listed"

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"




class Project(models.Model):
    guest_session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tech_stack = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='project_images/', null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class Experience(models.Model):
    guest_session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class Education(models.Model):
    guest_session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    board = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    score = models.CharField(max_length=10, null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class Achievement(models.Model):
    personal_details = models.ForeignKey(PersonalDetails, on_delete=models.CASCADE, null=True, blank=True)
    guest_session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    achievement = models.TextField(null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class Resume(models.Model):
     
    guest_session = models.OneToOneField(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


class OverallDescription(models.Model):
     
    guest_session = models.OneToOneField(GuestSession, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def get_owner_name(self):
        if self.guest_session:
            return self.guest_session.name
        return "Unknown"
    get_owner_name.short_description = "Name"


from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User

class ElitePage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = HTMLField()
    
    def __str__(self):
        return f"{self.user.username} – Elite Page"
