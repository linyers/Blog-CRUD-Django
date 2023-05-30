from django import forms
from .models import Post
from ckeditor.fields import RichTextField

class PostForm(forms.ModelForm):
    description = RichTextField()

    class Meta:
        model = Post
        fields = ['title', 'description']
        labels = {
            'title': 'Title',
            'description': ''
        }
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control'})
        }

class PostUpdateForm(forms.ModelForm):
    description = RichTextField()
    
    class Meta:
        model = Post
        fields = ['title', 'description']
        labels = {
            'title': 'Title',
            'description': ''
        }
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control'})
        }