import json
import os
from django.shortcuts import get_object_or_404, redirect ,render
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow


GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

REDIRECT_URI = "https://93f1-2409-40f3-109d-58ec-a11c-dbcb-b6e4-386b.ngrok-free.app/google/accounts/google/callback/"

def google_login(request):
    client_secrets_file = os.path.join(settings.BASE_DIR, 'testgoogle', 'client_secret.json')

    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=GOOGLE_SCOPES
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['state'] = state
    return redirect(authorization_url)


from django.contrib.auth import login
from django.shortcuts import redirect
from social_django.utils import psa

def google_callback(request):
    state = request.session.get('state')
    if not state:
        print("❌ No state found in session.")
        return redirect('/google/login-error/')

    print("✅ State from session:", state)

    client_secrets_file = os.path.join(settings.BASE_DIR, 'testgoogle', 'client_secret.json')
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=GOOGLE_SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    print("🌐 Authorization Response URL:", authorization_response)

    try:
        flow.fetch_token(authorization_response=authorization_response)
        print("✅ Access token fetched successfully.")
    except Exception as e:
        print("❌ Error fetching token:", str(e))
        return redirect('/google/login-error/')

    credentials = flow.credentials
    print("🔐 ID Token:", credentials.id_token)

    request_session = Request()

    try:
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request_session,
            settings.GOOGLE_CLIENT_ID
        )
        print("✅ ID Token verified successfully.")
        print("👤 User Info:", id_info)
    except ValueError as e:
        print("❌ Invalid ID Token:", str(e))
        return redirect('/google/login-error/')

    email = id_info.get("email")
    name = id_info.get("name", email.split("@")[0])  # Fallback if name is missing
    google_id = id_info.get("sub")
    profile_picture = id_info.get("picture")

    print(f"📧 Email: {email}, 🧑 Name: {name}, 🆔 Google ID: {google_id}")

    user, created = User.objects.get_or_create(email=email, defaults={'username': name})
    if created:
        print("🆕 New user created.")
    else:
        print("👤 Existing user found.")
        if not user.username:
            user.username = name
            user.save()
            print("✅ Username updated for existing user.")

    google_profile, _ = GoogleProfile.objects.get_or_create(user=user)
    if not google_profile.google_id:
        google_profile.google_id = google_id
        google_profile.profile_picture = profile_picture
        google_profile.save()
        print("🆕 Google profile updated.")

    # Login user and specify the backend
    login(request, user, backend='social_core.backends.google.GoogleOAuth2')

    print("✅ User logged in.")

    return redirect('/')  # Redirect to your app’s dashboard or homepage


from django.http import HttpResponse
def login_error(request):
    return HttpResponse("Google login failed. Please try again.")

import google.generativeai as genai
import os
from django.conf import settings

# Set your Gemini API key
genai.configure(api_key="AIzaSyBcN9e7DbsOmKKerD9G5m7Y5QJSGJCNiFM" )

def generate_page111(request):
    if request.method == "POST":
        name = request.POST.get("name")
        job = request.POST.get("job")
        about = request.POST.get("about")
        contact_email = request.POST.get("contact_email")
        section_title = request.POST.get("section_title")
        section_content = request.POST.get("section_content")
        prompt = request.POST.get("prompt")
        interests = request.POST.get("interests")
        colors = request.POST.get("colors")
        navbar = request.POST.get("navbar")
        navbar_links = request.POST.get("navbar_links")
        logo = request.FILES.get("logo")

        # Build design prompt dynamically based on form input
        design_prompt = f"""
        Generate a mobile-responsive HTML page using Tailwind CSS and Google Fonts. The page should be styled using the color palette: {colors}.

        The page layout should include:
        - A header section (with optional logo and navigation bar)
        - A hero section
        - An about section with user-provided text
        - A contact section with the user's email
        - An optional extra section based on the user's input

        Include the following details:
        - Name: {name}
        - Job Title: {job}
        - About: {about}
        - Contact Email: {contact_email}
        - Extra Section: {section_title}
        - Extra Section Content: {section_content}
        - Navbar: {navbar}
        - Navbar Links: {navbar_links}
        - Logo: {logo.name if logo else 'No logo provided'}

        The HTML output should:
        - Use Tailwind CSS classes for styling
        - Be fully responsive on mobile, tablet, and desktop
        - Include semantic HTML structure with sections like header, hero, about, contact, and footer
        - Ensure that all text elements are wrapped with class="editable" to enable editing via TinyMCE.
        Do not include any editor integration in the HTML itself.
        """
        
        # Use the model to generate the HTML content
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(design_prompt)

        # Extract only HTML and clean it
        generated_html = response.text.strip()

        # Pass the generated HTML to the template for rendering
        return render(request, 'main/out.html', {
            "generated_html": generated_html
        })

    return render(request, 'main/editor.html')

# views.py



from django.template import Template, Context
from django.shortcuts import render
import google.generativeai as genai

def generate_page(request):
    if request.method == 'POST':
        # === Step 1: Personal Details ===
        full_name = request.POST.get('full_name')
        title = request.POST.get('title')
        short_bio = request.POST.get('bio')
        location = request.POST.get('location')
        profile_image = request.FILES.get('profile_image')

        # === Step 2: Contact & Social Links ===
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        linkedin = request.POST.get('linkedin')
        github = request.POST.get('github')
        twitter = request.POST.get('twitter')
        website = request.POST.get('website')

        # === Step 3: Design Preferences ===
        primary_color = request.POST.get('primary_color')
        secondary_color = request.POST.get('secondary_color')
        design_style = request.POST.get('design_style')
        animation_style = request.POST.get('animation_style')

        # === Step 4: Device Preferences & Responsiveness ===
        devices = request.POST.getlist('devices[]')
        hamburger_menu = request.POST.get('hamburger_menu') == 'on'
        menu_items = request.POST.get('menu_items')
        navbar = request.POST.get('navbar')
        navbar_items = request.POST.get('navbar_items')
        footer_social = request.POST.get('footer_social')
        footer_contact = request.POST.get('footer_contact')

        # === Step 5: Skills ===
        skills = request.POST.get('skills')
        skills_list = [skill.strip() for skill in skills.split(',')] if skills else []

        # Gemini prompt
        prompt = f"""
Generate a responsive personal portfolio layout using Tailwind CSS.

Design Requirements:
- Primary color: {primary_color}
- Secondary color: {secondary_color}
- Design style: {design_style}
- Animation style: {animation_style}
- Supported devices: {', '.join(devices)}
- Hamburger menu: {"enabled" if hamburger_menu else "disabled"}
- Menu items: {menu_items}
- Navbar layout: {navbar} with items: {navbar_items}
- Footer must include social links: {footer_social} and contact info: {footer_contact}

Use these placeholders:
- {{% raw %}}{{ full_name }}, {{ title }}, {{ bio }}, {{ location }}, {{ profile_image }}
- {{ email }}, {{ phone }}, {{ linkedin }}, {{ github }}, {{ twitter }}, {{ website }}
- Loop: for skill in skills{{% endraw %}}

Instructions:
- Do NOT include any actual user data.
- Always include all sections listed, even if values might be empty.
- Use Django-style placeholders only.
- Return valid raw HTML using Tailwind CSS.
- Do not explain anything. Output only HTML.
"""

        print("📤 Sending prompt to Gemini...")
        try:
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content(prompt)
            generated_html = response.text.strip()

            # Remove Markdown if present
            if generated_html.startswith("```html") or generated_html.startswith("```"):
                generated_html = generated_html.strip("```html").strip("```").strip()

            # Fix placeholders: { full_name } → {{ full_name }}
            generated_html = generated_html.replace("{ ", "{{ ").replace(" }", " }}")

            print("✅ Gemini response received.")
        except Exception as e:
            print(f"❌ Error from Gemini API: {e}")
            generated_html = "<p>Error generating layout. Please try again.</p>"

        # Render with actual values
        return render(request, 'main/out.html', {
            "generated_html": generated_html,
            "full_name": full_name,
            "title": title,
            "bio": short_bio,
            "location": location,
            "profile_image": profile_image,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "twitter": twitter,
            "website": website,
            "skills": skills_list
        })

    return render(request, 'main/editor.html')




# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(f"uploaded_images/{image.name}", image)
        return JsonResponse({'url': fs.url(filename)})
    return JsonResponse({'error': 'Upload failed'}, status=400)



from django.http import JsonResponse
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import render

from django.http import JsonResponse
from .models import PersonalDetails, ContactInfo, DesignPreferences, DevicePreferences, Skill, Project, Experience, Education, Achievement, Resume
from authentication.models import GuestSession, GoogleUser, CustomUser
from django.utils import timezone

# Convert string to boolean
def str_to_bool(value):
    return True if value == 'yes' else False if value == 'no' else None

def get_current_guest_session(request):
    guest_token = request.session.get('guest_token')
    if guest_token:
        try:
            guest = GuestSession.objects.get(token=guest_token)
            guest.last_active = timezone.now()
            guest.save()
            return guest
        except GuestSession.DoesNotExist:
            pass
    return None


def testdata(request):
    if request.method == 'POST':
        guest = get_current_guest_session(request)
        
        # === Step 1: Personal Details ===
        full_name = request.POST.get('full_name')
        title = request.POST.get('title')
        short_bio = request.POST.get('bio')
        location = request.POST.get('location')
        profile_image = request.FILES.get('profile_image')

        personal_details, _ = PersonalDetails.objects.update_or_create(
            guest_session=guest,
            defaults={
                'full_name': full_name,
                'title': title,
                'short_bio': short_bio,
                'location': location,
                'profile_image': profile_image
            }
        )

        # === Step 2: Contact & Social Links ===
        contact_details, _ = ContactInfo.objects.update_or_create(
            guest_session=guest,
            defaults={
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'linkedin': request.POST.get('linkedin'),
                'github': request.POST.get('github'),
                'twitter': request.POST.get('twitter'),
                'website': request.POST.get('website'),
            }
        )

        # === Step 3: Design Preferences ===
        design_preferences, _ = DesignPreferences.objects.update_or_create(
            guest_session=guest,
            defaults={
                'primary_color': request.POST.get('primary_color'),
                'secondary_color': request.POST.get('secondary_color'),
                'design_style': request.POST.get('design_style'),
                'animation_style': request.POST.get('animation_style'),
            }
        )

        # === Step 4: Device Preferences ===
        devices = request.POST.getlist('devices[]')
        device_preferences, _ = DevicePreferences.objects.update_or_create(
            guest_session=guest,
            defaults={
                'devices': devices,
                'hamburger_menu': str_to_bool(request.POST.get('hamburger_menu')),
                'menu_items': request.POST.get('menu_items'),
                'navbar': str_to_bool(request.POST.get('navbar')),
                'navbar_items': request.POST.get('navbar_items'),
                'footer_enabled': str_to_bool(request.POST.get('footer_enabled')),
                'footer_social': str_to_bool(request.POST.get('footer_social')),
                'footer_contact': str_to_bool(request.POST.get('footer_contact'))
            }
        )

        # === Step 5: Skills ===
        skills_list = [s.strip() for s in request.POST.get('skills', '').split(',') if s.strip()]
        Skill.objects.update_or_create(
            guest_session=guest,
            defaults={'skills': skills_list}
        )

        # === Step 6: Projects ===
        i = 0
        while True:
            proj_title = request.POST.get(f'projects[{i}][title]')
            if not proj_title:
                break
            Project.objects.update_or_create(
                guest_session=guest,
                title=proj_title,
                defaults={
                    'description': request.POST.get(f'projects[{i}][description]', ''),
                    'tech_stack': request.POST.get(f'projects[{i}][tech_stack]', ''),
                    'link': request.POST.get(f'projects[{i}][link]', ''),
                    'image': request.FILES.get(f'projects[{i}][image]')
                }
            )
            i += 1

        # === Step 7: Experience ===
        i = 0
        while True:
            company = request.POST.get(f'experiences[{i}][company]')
            if not company:
                break
            Experience.objects.update_or_create(
                guest_session=guest,
                company=company,
                defaults={
                    'role': request.POST.get(f'experiences[{i}][role]', ''),
                    'duration': request.POST.get(f'experiences[{i}][duration]', '')
                }
            )
            i += 1

        # === Step 8: Education ===
        i = 0
        while True:
            institute = request.POST.get(f'education[{i}][institution]')
            if not institute:
                break
            Education.objects.update_or_create(
                guest_session=guest,
                institution=institute,
                defaults={
                    'course': request.POST.get(f'education[{i}][course]', ''),
                    'board': request.POST.get(f'education[{i}][board]', ''),
                    'year': request.POST.get(f'education[{i}][year]', ''),
                    'score': request.POST.get(f'education[{i}][score]', '')
                }
            )
            i += 1

        # === Step 9: Achievements ===
        i = 0
        while True:
            achievement = request.POST.get(f'achievements[{i}]')
            if not achievement:
                break
            Achievement.objects.update_or_create(
                guest_session=guest,
                achievement=achievement,
                defaults={}
            )
            i += 1

        # === Step 10: Resume & Hobbies ===
        Resume.objects.update_or_create(
            guest_session=guest,
            defaults={
                'resume': request.FILES.get('resume'),
                'hobbies': request.POST.get('hobbies')
            }
        )

        # === Step 11: Overall Description or Prompt ===
        overall_description = request.POST.get('overall_description')
        # Save if you have a model for this; otherwise, ignore

        return JsonResponse({
            'message': 'Form submitted and data saved successfully!',
            'owner_name': design_preferences.get_owner_name() if design_preferences else ''
        })

    return render(request, 'main/editor.html')




from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context
import google.generativeai as genai
import re
from bs4 import BeautifulSoup
import json
from django.template.loader import render_to_string
genai.configure(api_key="AIzaSyBcN9e7DbsOmKKerD9G5m7Y5QJSGJCNiFM")

# Helper to fix placeholders for Django templates
def fix_placeholders(html):
    return re.sub(r'\{ ?(\w+) ?\}', r'{{ \1 }}', html)

# Helper to add TinyMCE support
from bs4 import BeautifulSoup

def add_tinymce_classes(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Tags to be made editable with TinyMCE
    editable_tags = ['p', 'h1', 'h2', 'h3']
    
    # Apply the 'editable' class to text tags
    for tag in soup.find_all(editable_tags):
        existing_classes = tag.get('class', [])
        if 'editable' not in existing_classes:
            tag['class'] = existing_classes + ['editable']
    
    # Apply the 'editable-image' class to image tags
    for img in soup.find_all('img'):
        existing_classes = img.get('class', [])
        if 'editable-image' not in existing_classes:
            img['class'] = existing_classes + ['editable-image']
    
    return str(soup)


# Helper to strip ```html fences from Gemini output
def strip_code_fences(html):
    return re.sub(r"^```html\n?|```$", "", html.strip())

# Main view
def editor(request):
    if request.method == "GET":
        return render(request, "main/editor.html")  # Show input form

    # === Collect data ===
    full_name = request.POST.get('full_name')
    title = request.POST.get('title')
    short_bio = request.POST.get('bio')
    location = request.POST.get('location')
    profile_image = request.FILES.get('profile_image')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    linkedin = request.POST.get('linkedin')
    github = request.POST.get('github')
    twitter = request.POST.get('twitter')
    website = request.POST.get('website')
    primary_color = request.POST.get('primary_color')
    secondary_color = request.POST.get('secondary_color')
    design_style = request.POST.get('design_style')
    animation_style = request.POST.get('animation_style')
    devices = request.POST.getlist('devices[]')
    hamburger_menu = request.POST.get('hamburger_menu') == 'on'
    menu_items = request.POST.get('menu_items')
    navbar = request.POST.get('navbar')
    navbar_items = request.POST.get('navbar_items')
    footer_social = request.POST.get('footer_social')
    footer_contact = request.POST.get('footer_contact')
    skills = request.POST.get('skills')
    skills_list = [s.strip() for s in skills.split(',')] if skills else []

    # === Debugging ===
    print("[DEBUG] Skills raw input:", skills)
    print("[DEBUG] Skills list:", skills_list)

    # === Context for rendering ===
    context = {
        "full_name": full_name,
        "title": title,
        "bio": short_bio,
        "location": location,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "twitter": twitter,
        "website": website,
        "skills": skills_list,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "navbar_layout": navbar,
        "menu_items": menu_items,
        "footer_social_links": footer_social,
        "footer_contact_info": footer_contact,
    }

    # === Gemini Prompt ===
    prompt = f"""
Generate a complete, clean HTML layout for a personal portfolio using Tailwind CSS.

Requirements:
- Primary color: {primary_color}
- Secondary color: {secondary_color}
- Design style: {design_style}
- Animation style: {animation_style}
- Devices: {", ".join(devices)}
- Hamburger menu: {"enabled" if hamburger_menu else "disabled"}
- Menu items: {menu_items}
- Navbar layout: {navbar}
- Footer should contain social links: {footer_social} and contact info: {footer_contact}
- Must include a skills section looping over {{% for skill in skills %}}.
- Use placeholders like {{ full_name }}, {{ title }}, {{ bio }}, etc.
- Only output pure valid HTML with no comments, explanations, key improvements, or markdown fences.
"""

    print("[DEBUG] Prompt sent to Gemini:\n", prompt)

    # === Gemini HTML Generation ===
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    html = response.text

    print("[DEBUG] Raw Gemini Output:\n", html[:10000])

    # === Clean & Process HTML ===
    html = strip_code_fences(html)
    html = fix_placeholders(html)
    html = add_tinymce_classes(html)

    print("[DEBUG] Final Processed HTML:\n", html[:10000])

    # === Render HTML with Django Template Engine ===
    template = Template(html)
    rendered_html = template.render(Context(context))

# Now render `out.html` and inject `rendered_html` into it
    final_page = render_to_string("main/out.html", {"generated_html": rendered_html})

    return HttpResponse(final_page)



def sendwebtest(request):
    # Fetch all data from the models
    personal_details = PersonalDetails.objects.all()
    contact_details = ContactInfo.objects.all()
    design_preferences = DesignPreferences.objects.all()
    device_preferences = DevicePreferences.objects.all()
    skills = Skill.objects.all()
    projects = Project.objects.all()
    experiences = Experience.objects.all()
    education = Education.objects.all()
    achievements = Achievement.objects.all()
    resumes = Resume.objects.all()
    
    # Get current year for footer
    from datetime import datetime
    current_year = datetime.now().year
    
    context = {
        'personal_details': personal_details,
        'contact_details': contact_details,
        'design_preferences': design_preferences,
        'device_preferences': device_preferences,
        'skills': skills,
        'projects': projects,
        'experiences': experiences,
        'education': education,
        'achievements': achievements,
        'resumes': resumes,
        'current_year': current_year,
    }
    
    return render(request, "porttemp/portfolio.html", context)


from django.shortcuts import render

def portfoliofree(request):
    context = {
        'developer_name': 'Alex Johnson',
        'job_title': 'Frontend Developer & UI Enthusiast',
        'short_bio': 'I build accessible, user-friendly web experiences with modern technologies. Passionate about clean code and thoughtful design.',
        'primary_color': '#2563eb',
        'secondary_color': '#059669',
        'projects': [
            {
                'title': 'E-commerce Dashboard',
                'description': 'A responsive admin dashboard for e-commerce analytics built with React and Chart.js.',
                'tags': ['React', 'JavaScript', 'Chart.js'],
                'link': '#'
            },
            {
                'title': 'Task Management App',
                'description': 'A collaborative task management application with real-time updates using Django and WebSockets.',
                'tags': ['Django', 'Python', 'WebSockets'],
                'link': '#'
            },
            {
                'title': 'Portfolio Website',
                'description': 'A minimalist portfolio website with dark mode toggle and animated transitions.',
                'tags': ['HTML/CSS', 'JavaScript', 'GSAP'],
                'link': '#'
            }
        ],
        'contact_message': "I'm always open to discussing new projects or opportunities. Don't hesitate to reach out!",
        'social_links': {
            'email': 'alex@example.com',
            'github': 'https://github.com/username',
            'linkedin': 'https://linkedin.com/in/username',
            'twitter': 'https://twitter.com/username'
        }
    }
    return render(request, "porttemp/portfolio.html", context)




from django.shortcuts import render, redirect
from .forms import ElitePageForm
from .models import ElitePage

def create_elite_page(request):
    if request.method == 'POST':
        form = ElitePageForm(request.POST)
        if form.is_valid():
            elite_page = form.save(commit=False)
            elite_page.user = request.user
            elite_page.save()
            return redirect('view_elite_page', elite_page.id)
    else:
        form = ElitePageForm()
    return render(request, 'elite/create_page.html', {'form': form})

def view_elite_page(request, pk):
    page = ElitePage.objects.get(pk=pk)
    return render(request, 'elite/view_page.html', {'page': page})

# portfolio/views.py
from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from django.conf import settings

# Set your Gemini API Key
genai.configure(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
def generate_content(request):
    if request.method == "POST":
        prompt = request.POST.get("user_prompt", "")
        if prompt:
            try:
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                response = model.generate_content(prompt)
                return JsonResponse({"generated_content": response.text})
            except Exception as e:
                return JsonResponse({"error": str(e)})
        return JsonResponse({"error": "Prompt is empty."})
    return JsonResponse({"error": "Invalid method"})


from django.shortcuts import render
from .models import *

from django.shortcuts import render

from authentication.models import GuestSession,CustomUser,GoogleUser
from django.utils import timezone
from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from .models import (
   
    PersonalDetails, ContactInfo, DesignPreferences,
    DevicePreferences, Skill, Project, Experience,
    Education, Achievement, Resume, OverallDescription
)

def all_data_view(request):
    print("SESSION DATA:", dict(request.session))

    user = None
    user_id = request.session.get('user_id')
    guest_token = request.session.get('guest_token')
    guest_session = None

    # Try to authenticate user
    if user_id:
        try:
            user = GoogleUser.objects.get(id=user_id)
            print("Authenticated as GoogleUser:", user)
        except GoogleUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(id=user_id)
                print("Authenticated as CustomUser:", user)
            except CustomUser.DoesNotExist:
                print("User ID not found in either model.")

    # If not authenticated, check guest session
    if not user and guest_token:
        try:
            guest_session = GuestSession.objects.get(token=guest_token)
            print("Guest token:", guest_session.token)

            # Update last active time
            guest_session.last_active = timezone.now()
            guest_session.save()
        except GuestSession.DoesNotExist:
            print("Invalid guest token.")

    # Prepare filtered context
    context = {}

    if user:
        # Filter by user (assuming these models support a `user` FK)
        context = {
            'personal_details': PersonalDetails.objects.filter(guest_session=None),  # For demo, if user data not linked
            'contact_info': ContactInfo.objects.filter(guest_session=None),
            'design_preferences': DesignPreferences.objects.filter(guest_session=None),
            'device_preferences': DevicePreferences.objects.filter(guest_session=None),
            'skills': Skill.objects.filter(guest_session=None),
            'projects': Project.objects.filter(guest_session=None),
            'experiences': Experience.objects.filter(guest_session=None),
            'education': Education.objects.filter(guest_session=None),
            'achievements': Achievement.objects.filter(guest_session=None),
            'resumes': Resume.objects.filter(guest_session=None),
            'overall_descriptions': OverallDescription.objects.filter(guest_session=None),
            'user': user
        }
    elif guest_session:
        # Filter all models by guest_session FK
        context = {
            'personal_details': PersonalDetails.objects.filter(guest_session=guest_session),
            'contact_info': ContactInfo.objects.filter(guest_session=guest_session),
            'design_preferences': DesignPreferences.objects.filter(guest_session=guest_session),
            'device_preferences': DevicePreferences.objects.filter(guest_session=guest_session),
            'skills': Skill.objects.filter(guest_session=guest_session),
            'projects': Project.objects.filter(guest_session=guest_session),
            'experiences': Experience.objects.filter(guest_session=guest_session),
            'education': Education.objects.filter(guest_session=guest_session),
            'achievements': Achievement.objects.filter(guest_session=guest_session),
            'resumes': Resume.objects.filter(guest_session=guest_session),
            'overall_descriptions': OverallDescription.objects.filter(guest_session=guest_session),
            'user': None
        }
    else:
        print("No user or valid guest session found.")

    return render(request, "porttemp/portfolio.html", context)


from django.core.files.storage import FileSystemStorage

def project_manage_view(request):
    user_id = request.session.get('user_id')
    guest_token = request.session.get('guest_token')
    user = guest_session = None

    if user_id:
        user = CustomUser.objects.filter(id=user_id).first()
        projects = Project.objects.filter(user=user)
    elif guest_token:
        guest_session = GuestSession.objects.filter(token=guest_token).first()
        projects = Project.objects.filter(guest_session=guest_session)
    else:
        return redirect('home')

    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        tech_stack = request.POST.get('tech_stack')
        link = request.POST.get('link')
        image = request.FILES.get('image')

        # Handle project deletion
        if 'delete' in request.POST:
            project = get_object_or_404(Project, id=project_id)
            if (user and project.user_id == user.id) or (guest_session and project.guest_session_id == guest_session.id):
                project.delete()
            return redirect('project_manage')

        # Handle project update or add
        if project_id:  # Update existing project
            project = get_object_or_404(Project, id=project_id)
            if (user and project.user_id == user.id) or (guest_session and project.guest_session_id == guest_session.id):
                project.title = title
                project.description = description
                project.tech_stack = tech_stack
                project.link = link
                if image:
                    project.image = image
                project.save()
        else:  # Add new project
            project = Project(
                title=title,
                description=description,
                tech_stack=tech_stack,
                link=link,
                image=image
            )
            if user:
                project.user = user
            elif guest_session:
                project.guest_session = guest_session
            project.save()

        return redirect('project_manage')

    return render(request, 'porttemp/project_manage.html', {'projects': projects, 'project_count': projects.count()})


def resume_manage_view(request):
    user_id = request.session.get('user_id')
    guest_token = request.session.get('guest_token')
    user = guest_session = None

    if user_id:
        user = CustomUser.objects.filter(id=user_id).first()
        resumes = Resume.objects.filter(user=user)
    elif guest_token:
        guest_session = GuestSession.objects.filter(token=guest_token).first()
        resumes = Resume.objects.filter(guest_session=guest_session)
    else:
        return redirect('home')

    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        hobbies = request.POST.get('hobbies')
        resume_file = request.FILES.get('resume')

        # Handle resume deletion
        if 'delete' in request.POST:
            resume = get_object_or_404(Resume, id=resume_id)
            if (user and resume.user_id == user.id) or (guest_session and resume.guest_session_id == guest_session.id):
                resume.delete()
            return redirect('resume_manage')

        # Handle resume update or add
        if resume_id:  # Update existing resume
            resume = get_object_or_404(Resume, id=resume_id)
            if (user and resume.user_id == user.id) or (guest_session and resume.guest_session_id == guest_session.id):
                resume.hobbies = hobbies
                if resume_file:
                    resume.resume = resume_file
                resume.save()
        else:  # Add new resume
            resume = Resume(
                hobbies=hobbies,
                resume=resume_file
            )
            if user:
                resume.user = user
            elif guest_session:
                resume.guest_session = guest_session
            resume.save()

        return redirect('resume_manage')

    return render(request, 'porttemp/resume_manage.html', {'resumes': resumes, 'resume_count': resumes.count()})





def manage_content_view(request):
    user_id = request.session.get('user_id')
    guest_token = request.session.get('guest_token')
    user = guest_session = None

    if user_id:
        user = CustomUser.objects.filter(id=user_id).first()
        projects = Project.objects.filter(user=user)
        resumes = Resume.objects.filter(user=user)
    elif guest_token:
        guest_session = GuestSession.objects.filter(token=guest_token).first()
        projects = Project.objects.filter(guest_session=guest_session)
        resumes = Resume.objects.filter(guest_session=guest_session)
    else:
        return redirect('home')

    if request.method == 'POST':
        if 'delete_project' in request.POST:
            project = get_object_or_404(Project, id=request.POST.get('delete_project'))
            if (user and project.user_id == user.id) or (guest_session and project.guest_session_id == guest_session.id):
                project.delete()

        elif 'edit_project' in request.POST or 'new_project' in request.POST:
            project_id = request.POST.get('edit_project')
            title = request.POST.get('title')
            description = request.POST.get('description')
            tech_stack = request.POST.get('tech_stack')
            link = request.POST.get('link')
            image = request.FILES.get('image')

            if project_id:
                project = get_object_or_404(Project, id=project_id)
                if (user and project.user_id == user.id) or (guest_session and project.guest_session_id == guest_session.id):
                    project.title = title
                    project.description = description
                    project.tech_stack = tech_stack
                    project.link = link
                    if image:
                        project.image = image
                    project.save()
            else:
                project = Project(title=title, description=description, tech_stack=tech_stack, link=link, image=image)
                if user:
                    project.user = user
                else:
                    project.guest_session = guest_session
                project.save()

        elif 'delete_resume' in request.POST:
            resume = get_object_or_404(Resume, id=request.POST.get('delete_resume'))
            if (user and resume.user_id == user.id) or (guest_session and resume.guest_session_id == guest_session.id):
                resume.delete()

        elif 'edit_resume' in request.POST or 'new_resume' in request.POST:
            resume_id = request.POST.get('edit_resume')
            hobbies = request.POST.get('hobbies')
            resume_file = request.FILES.get('resume')

            if resume_id:
                resume = get_object_or_404(Resume, id=resume_id)
                if (user and resume.user_id == user.id) or (guest_session and resume.guest_session_id == guest_session.id):
                    resume.hobbies = hobbies
                    if resume_file:
                        resume.resume = resume_file
                    resume.save()
            else:
                resume = Resume(hobbies=hobbies, resume=resume_file)
                if user:
                    resume.user = user
                else:
                    resume.guest_session = guest_session
                resume.save()

        return redirect('project_manage')

    return render(request, "porttemp/project_manage.html", {
        'projects': projects,
        'resumes': resumes,
        'project_count': projects.count(),
        'resume_count': resumes.count(),
    })




from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
import json
from uuid import UUID

def get_guest_session(request):
    """Utility function to get or create guest session"""
    guest_token = request.session.get('guest_token')
    if not guest_token:
        return None
    return get_object_or_404(GuestSession, token=guest_token)

def dashboard_view(request):
    guest_session = get_guest_session(request)
    if not guest_session:
        return redirect('home')
    
    # Get all related data
    personal_details = PersonalDetails.objects.filter(guest_session=guest_session).first()
    contact_info = ContactInfo.objects.filter(guest_session=guest_session).first()
    projects = Project.objects.filter(guest_session=guest_session)
    experiences = Experience.objects.filter(guest_session=guest_session)
    educations = Education.objects.filter(guest_session=guest_session)
    achievements = Achievement.objects.filter(guest_session=guest_session)
    resume = Resume.objects.filter(guest_session=guest_session).first()
    skills = Skill.objects.filter(guest_session=guest_session).first()
    
    # Determine display name
    if personal_details and personal_details.full_name:
        display_name = personal_details.full_name
    else:
        display_name = guest_session.name
    
    context = {
        'guest': guest_session,
        'personal_details': personal_details,
        'contact_info': contact_info,
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
        'achievements': achievements,
        'resume': resume,
        'skills': skills.get_skills() if skills else [],
        'display_name': display_name,
    }
    return render(request, 'dashboard/dashboard.html', context)


@require_http_methods(["POST"])
def save_personal_details(request):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)
    
    data = json.loads(request.body)
    
    personal_details, created = PersonalDetails.objects.get_or_create(
        guest_session=guest_session,
        defaults={
            'full_name': data.get('full_name', ''),
            'title': data.get('title', ''),
            'short_bio': data.get('short_bio', ''),
            'location': data.get('location', ''),
        }
    )
    
    if not created:
        personal_details.full_name = data.get('full_name', personal_details.full_name)
        personal_details.title = data.get('title', personal_details.title)
        personal_details.short_bio = data.get('short_bio', personal_details.short_bio)
        personal_details.location = data.get('location', personal_details.location)
        personal_details.save()
    
    return JsonResponse({'status': 'success'})

@require_http_methods(["POST"])
def save_contact_info(request):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)
    
    data = json.loads(request.body)
    
    contact_info, created = ContactInfo.objects.get_or_create(
        guest_session=guest_session,
        defaults={
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'linkedin': data.get('linkedin', ''),
            'github': data.get('github', ''),
            'twitter': data.get('twitter', ''),
            'website': data.get('website', ''),
        }
    )
    
    if not created:
        contact_info.email = data.get('email', contact_info.email)
        contact_info.phone = data.get('phone', contact_info.phone)
        contact_info.linkedin = data.get('linkedin', contact_info.linkedin)
        contact_info.github = data.get('github', contact_info.github)
        contact_info.twitter = data.get('twitter', contact_info.twitter)
        contact_info.website = data.get('website', contact_info.website)
        contact_info.save()
    
    return JsonResponse({'status': 'success'})

@require_http_methods(["POST"])
def add_project(request):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)
    
    data = json.loads(request.body)
    
    project = Project.objects.create(
        guest_session=guest_session,
        title=data.get('title', ''),
        description=data.get('description', ''),
        tech_stack=data.get('tech_stack', ''),
        link=data.get('link', ''),
    )
    
    return JsonResponse({'status': 'success', 'id': project.id})

@require_http_methods(["POST"])
def update_project(request, project_id):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)
    
    try:
        project = Project.objects.get(id=project_id, guest_session=guest_session)
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)
    
    data = json.loads(request.body)
    
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.tech_stack = data.get('tech_stack', project.tech_stack)
    project.link = data.get('link', project.link)
    project.save()
    
    return JsonResponse({'status': 'success'})

@require_http_methods(["DELETE"])
def delete_project(request, project_id):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)
    
    try:
        project = Project.objects.get(id=project_id, guest_session=guest_session)
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)
    
    project.delete()
    return JsonResponse({'status': 'success'})

# Similar views for Experience, Education, Achievement, Resume, Skill would follow the same pattern
# For brevity, I'm showing the pattern with Project, but you would implement similar views for other models


@require_http_methods(["POST"])
def add_skill(request):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)

    data = json.loads(request.body)
    name = data.get('name', '').strip()
    try:
        level = int(data.get('level', 5))
        if not (1 <= level <= 10):
            raise ValueError()
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid skill level'}, status=400)

    skill_obj, _ = Skill.objects.get_or_create(guest_session=guest_session)

    skills_list = skill_obj.get_skills()
    skills_list.append({'name': name, 'level': level})
    skill_obj.set_skills(skills_list)
    skill_obj.save()

    return JsonResponse({'status': 'success'})


@require_http_methods(["POST"])
def update_skill(request, skill_index):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)

    try:
        skill_obj = Skill.objects.get(guest_session=guest_session)
    except Skill.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Skills not found'}, status=404)

    skills_list = skill_obj.get_skills()

    if not (0 <= skill_index < len(skills_list)):
        return JsonResponse({'status': 'error', 'message': 'Invalid index'}, status=400)

    data = json.loads(request.body)
    try:
        skills_list[skill_index]['name'] = data.get('name', skills_list[skill_index]['name']).strip()
        skills_list[skill_index]['level'] = int(data.get('level', skills_list[skill_index]['level']))
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid skill data'}, status=400)

    skill_obj.set_skills(skills_list)
    skill_obj.save()

    return JsonResponse({'status': 'success'})


@require_http_methods(["DELETE"])
def delete_skill(request, skill_index):
    guest_session = get_guest_session(request)
    if not guest_session:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'}, status=400)

    try:
        skill_obj = Skill.objects.get(guest_session=guest_session)
    except Skill.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Skills not found'}, status=404)

    skills_list = skill_obj.get_skills()

    if not (0 <= skill_index < len(skills_list)):
        return JsonResponse({'status': 'error', 'message': 'Invalid index'}, status=400)

    skills_list.pop(skill_index)
    skill_obj.set_skills(skills_list)
    skill_obj.save()

    return JsonResponse({'status': 'success'})