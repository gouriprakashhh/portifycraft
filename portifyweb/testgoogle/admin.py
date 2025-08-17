from django.contrib import admin
from .models import (
    PersonalDetails,
    ContactInfo,
    DesignPreferences,
    DevicePreferences,
    Skill,
    Project,
    Experience,
    Education,
    Achievement,
    Resume,
    OverallDescription,
)

class PersonalDetailsAdmin(admin.ModelAdmin):
    list_display = ('get_owner_name','full_name')  # Display UUID and Full Name

class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'email', 'phone')  # Display ID, related PersonalDetails, and email/phone

class DesignPreferencesAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'primary_color', 'design_style')

class DevicePreferencesAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'devices', 'navbar')  # Display ID, related PersonalDetails, and device preferences

class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name')  # Display ID, related PersonalDetails, and skill

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'title', 'tech_stack')  # Display ID, related PersonalDetails, and project title

class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'company', 'role')  # Display ID, related PersonalDetails, and company/role

class EducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'institution', 'course')  # Display ID, related PersonalDetails, and institution/course

class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'achievement')  # Display ID, related PersonalDetails, and achievement

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'resume', 'hobbies')  # Display ID, related PersonalDetails, and resume/hobbies

class OverallDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner_name', 'description')  # Display ID, related PersonalDetails, and description

# Register each model with their respective ModelAdmin class
admin.site.register(PersonalDetails, PersonalDetailsAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(DesignPreferences, DesignPreferencesAdmin)
admin.site.register(DevicePreferences, DevicePreferencesAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Resume, ResumeAdmin)
admin.site.register(OverallDescription, OverallDescriptionAdmin)

