from django import forms
from .models import ElitePage
from tinymce.widgets import TinyMCE

class ElitePageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(
        attrs={'cols': 80, 'rows': 30}
    ))

    class Meta:
        model = ElitePage
        fields = ['title', 'content']

# forms.py
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']  # ONLY include relevant fields
