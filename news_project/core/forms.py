from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Publisher, CustomUser, Article, Newsletter


class SubscriptionForm(forms.Form):
    """
    Form for readers to manage their subscriptions.

    Allows selection of multiple publishers and journalists.
    Both fields are optional.
    """
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    journalists = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='journalist'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class ArticleForm(forms.ModelForm):
    """
    Form for journalists to create or edit articles.

    Includes fields for:
    - Title (text input)
    - Content (text area)
    - Publisher (dropdown select)

    Uses Bootstrap-compatible widgets for styling.
    """
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'})
        }


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with role selection.

    Extends Django's built-in UserCreationForm and adds:
    - Role field (reader, journalist, editor or publisher)
    - Bootstrap widgets for form styling

    On save:
    - Sets the role of the user
    - Adds the user to the corresponding Django group
    ('Reader', 'Journalist', 'Editor' or 'Publisher')
    """
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('journalist', 'Journalist'),
        ('publisher', 'Publisher'),
        ('editor', 'Editor')
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']

        if role == 'reader':
            user.role = 'reader'
        elif role == 'journalist':
            user.role = 'journalist'
        elif role == 'publisher':
            user.role = 'publisher'
        elif role == 'editor':
            user.role = 'editor'

        if commit:
            user.save()
            # Assign to group
            from django.contrib.auth.models import Group
            # e.g., 'Reader', 'Journalist', 'editor' or 'Publisher'
            group = Group.objects.get(name=role.capitalize())
            user.groups.add(group)
        return user


class NewsletterForm(forms.ModelForm):
    """
    Form for journalists to create newsletters.

    Includes:
    - Title (text input)
    - Body/content (text area)
    - Publisher selection (dropdown select)

    Applies Bootstrap styling to all fields.
    """
    class Meta:
        model = Newsletter
        fields = ['title', 'body', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'})
        }
