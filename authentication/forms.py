# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# def SignupDomainValidator(value):
#     ALLOWED_SIGNUP_DOMAINS = ['*']
#     if '*' not in ALLOWED_SIGNUP_DOMAINS:
#         try:
#             domain = value[value.index("@"):]
#             if domain not in ALLOWED_SIGNUP_DOMAINS:
#                 raise ValidationError(u'Invalid domain. Allowed domains on this network: {0}'.format(','.join(ALLOWED_SIGNUP_DOMAINS)))
#         except Exception:
#             raise ValidationError(u'Invalid domain. Allowed domains on this network: {0}'.format(','.join(ALLOWED_SIGNUP_DOMAINS)))

# def ForbiddenUsernamesValidator(value):
#     forbidden_usernames = ['admin', 'settings', 'news', 'about', 'help', 'signin', 'signup', 
#         'signout', 'terms', 'privacy', 'cookie', 'new', 'login', 'logout', 'administrator', 
#         'join', 'account', 'username', 'root', 'blog', 'user', 'users', 'billing', 'subscribe',
#         'reviews', 'review', 'blog', 'blogs', 'edit', 'mail', 'email', 'home', 'job', 'jobs', 
#         'contribute', 'newsletter', 'shop', 'profile', 'register', 'auth', 'authentication',
#         'campaign', 'config', 'delete', 'remove', 'forum', 'forums', 'download', 'downloads', 
#         'contact', 'blogs', 'feed', 'feeds', 'faq', 'intranet', 'log', 'registration', 'search', 
#         'explore', 'rss', 'support', 'status', 'static', 'media', 'setting', 'css', 'js',
#         'follow', 'activity', 'questions', 'articles', 'network',]
#     if value.lower() in forbidden_usernames:
#         raise ValidationError('This is a reserved word.')

# def InvalidUsernameValidator(value):
#     if '@' in value or '+' in value or '-' in value:
#         raise ValidationError('Enter a valid username.')

# def UniqueEmailValidator(value):
#     if User.objects.filter(email__iexact=value).exists():
#         raise ValidationError('User with this Email already exists.')

# def UniqueUsernameIgnoreCaseValidator(value):
#     if User.objects.filter(username__iexact=value).exists():
#         raise ValidationError('User with this Username already exists.')

# class SignUpForm(forms.ModelForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
#         max_length=30,
#         required=True,
#         help_text='Usernames may contain <strong>alphanumeric</strong>, <strong>_</strong> and <strong>.</strong> characters')
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
#     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
#         label="Confirm your password",
#         required=True)
#     email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control'}), 
#         required=True,
#         max_length=75)

#     class Meta:
#         model = User
#         exclude = ['last_login', 'date_joined']
#         fields = ['username', 'email', 'password', 'confirm_password',]

#     def __init__(self, *args, **kwargs):
#         super(SignUpForm, self).__init__(*args, **kwargs)
#         self.fields['username'].validators.append(ForbiddenUsernamesValidator)
#         self.fields['username'].validators.append(InvalidUsernameValidator)
#         self.fields['username'].validators.append(UniqueUsernameIgnoreCaseValidator)
#         self.fields['email'].validators.append(UniqueEmailValidator)
#         self.fields['email'].validators.append(SignupDomainValidator)

#     def clean(self):
#         super(SignUpForm, self).clean()
#         password = self.cleaned_data.get('password')
#         confirm_password = self.cleaned_data.get('confirm_password')
#         if password and password != confirm_password:
#             self._errors['password'] = self.error_class(['Passwords don\'t match'])
#         return self.cleaned_data


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def uniqueemailvalidator(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError('Пользователь с этой почтой уже существует')

    def forbiddenusernamesvalidator(self, value):
        forbidden_usernames = ['admin', 'settings', 'news', 'about', 'help', 'signin', 'signup', 
            'signout', 'terms', 'privacy', 'cookie', 'new', 'login', 'logout', 'administrator', 
            'join', 'account', 'username', 'root', 'blog', 'user', 'users', 'billing', 'subscribe',
            'reviews', 'review', 'blog', 'blogs', 'edit', 'mail', 'email', 'home', 'job', 'jobs', 
            'contribute', 'newsletter', 'shop', 'profile', 'register', 'auth', 'authentication',
            'campaign', 'config', 'delete', 'remove', 'forum', 'forums', 'download', 'downloads', 
            'contact', 'blogs', 'feed', 'feeds', 'faq', 'intranet', 'log', 'registration', 'search', 
            'explore', 'rss', 'support', 'status', 'static', 'media', 'setting', 'css', 'js',
            'follow', 'activity', 'questions', 'articles', 'users',]
        if value.lower() in forbidden_usernames:
            raise ValidationError('Это системное имя')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators.append(self.forbiddenusernamesvalidator)
        self.fields['email'].validators.append(self.uniqueemailvalidator)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1','password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user