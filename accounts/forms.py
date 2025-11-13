from django import forms 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import CustomUser, Contestant


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-input'
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-input'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-input'
        })
    )
    
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'agreement-checkbox'
        }),
        label='I agree to the Participation Agreement'
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check for case-insensitive username uniqueness
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        
        # Additional username validation
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        if len(username) > 30:
            raise forms.ValidationError("Username must be 30 characters or less.")
        
        if not username.replace('_', '').replace('-', '').isalnum():
            raise forms.ValidationError("Username can only contain letters, numbers, underscores, and hyphens.")
        
        # Check for reserved usernames
        reserved_usernames = ['admin', 'administrator', 'root', 'api', 'www', 'mail', 'email', 'support', 'help', 'contact']
        if username.lower() in reserved_usernames:
            raise forms.ValidationError("This username is reserved and cannot be used.")
        
        return username
    
    def clean_agree_to_terms(self):
        agree_to_terms = self.cleaned_data.get('agree_to_terms')
        if not agree_to_terms:
            raise forms.ValidationError("You must agree to the Participation Agreement to create an account.")
        return agree_to_terms

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input'
        })
    )

class UserSettingsForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Tell us about yourself...',
            'rows': 4
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'bio', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check for case-insensitive username uniqueness (excluding current user)
        if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this username already exists.")
        
        # Additional username validation
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        if len(username) > 30:
            raise forms.ValidationError("Username must be 30 characters or less.")
        
        if not username.replace('_', '').replace('-', '').isalnum():
            raise forms.ValidationError("Username can only contain letters, numbers, underscores, and hyphens.")
        
        # Check for reserved usernames
        reserved_usernames = ['admin', 'administrator', 'root', 'api', 'www', 'mail', 'email', 'support', 'help', 'contact']
        if username.lower() in reserved_usernames:
            raise forms.ValidationError("This username is reserved and cannot be used.")
        
        return username

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Current password'
        })
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'New password'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("New passwords don't match.")
            if len(new_password1) < 8:
                raise forms.ValidationError("New password must be at least 8 characters long.")
        return cleaned_data

class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password to confirm deletion'
        }),
        help_text="Enter your current password to confirm account deletion"
    )
    
    confirm_deletion = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'delete-checkbox'
        }),
        required=True,
        help_text="I understand that deleting my account is permanent and cannot be undone"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email__iexact=email).exists():
            # Don't reveal if email exists for security
            pass
        return email

class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter new email address'
        }),
        label='New Email Address'
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password to confirm'
        }),
        label='Confirm Password',
        help_text='Enter your current password to confirm the email change'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if not new_email:
            return new_email
        
        # Check if email is different from current
        if new_email.lower() == self.user.email.lower():
            raise forms.ValidationError("This is already your current email address.")
        
        # Check if email already exists
        if CustomUser.objects.filter(email__iexact=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        
        return new_email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password. Please enter your current password.")
        return password

class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'New password'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Passwords don't match.")
            if len(new_password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
        return cleaned_data

class ContestantSubmissionForm(forms.ModelForm):
    submission_type = forms.ChoiceField(
        choices=Contestant.SUBMISSION_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'submission-type-radio'}),
        initial='video'
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your submission title'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Describe your talent submission...',
            'rows': 4
        })
    )
    
    video_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-input',
            'placeholder': 'Or paste a video URL (YouTube, Vimeo, etc.)'
        })
    )
    
    video_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'video/*'
        })
    )
    
    image_file = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Contestant
        fields = ['submission_type', 'title', 'description', 'video_url', 'video_file', 'image_file']
    
    def clean(self):
        cleaned_data = super().clean()
        submission_type = cleaned_data.get('submission_type')
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        image_file = cleaned_data.get('image_file')
        
        if submission_type == 'video':
            if not video_url and not video_file:
                raise forms.ValidationError("Please provide either a video URL or upload a video file.")
            if video_url and video_file:
                raise forms.ValidationError("Please provide either a video URL or a video file, not both.")
        elif submission_type == 'image':
            if not image_file:
                raise forms.ValidationError("Please upload an image file.")
        
        return cleaned_data
