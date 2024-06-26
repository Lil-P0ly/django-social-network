# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=30,label="Имя",required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=30,label="Фамилия",
        required=False)
    job_title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=50,label="Интересы",
        required=False)
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=75,label="Email",
        required=False)
    url = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), 
        max_length=50,
        label="Курс №",
        required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=50,label="Факультет",
        required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'job_title', 'email', 'url', 'location',]


class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
        label="Старый пароль",
        required=True)

    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
        label="Новый пароль",
        required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
        label="Повторите новый пароль",
        required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class(['Неверный старый пароль'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class(['Пароли не совпадают'])
        return self.cleaned_data