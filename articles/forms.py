# -*- coding: utf-8 -*-
from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label='Название',
        max_length=255)
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), label='Описание',
        max_length=4000)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label='Теги',
        max_length=255,
        required=False,
        help_text='Используйте пробелы, чтобы разделить теги')

    class Meta:
        model = Article
        fields = ['title', 'content', 'tags', 'status']
