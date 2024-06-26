# -*- coding: utf-8 -*-
from django import forms
from questions.models import Question, Answer

class QuestionForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label = 'Название',
        max_length=255)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), label = 'Описание',
        max_length=2000)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label = 'Теги',
        max_length=255,
        required=False,
        help_text='Используйте пробелы, чтобы разделить теги')

    class Meta:
        model = Question
        fields = ['title', 'description', 'tags']

class AnswerForm(forms.ModelForm):
    question = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Question.objects.all())
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':'4'}), 
        max_length=2000)

    class Meta:
        model = Answer
        fields = ['question', 'description']