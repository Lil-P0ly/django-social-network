# coding: utf-8

from django.conf.urls import url #patterns, include, url

from articles import views

urlpatterns = [
    url(r'^$', views.articles, name='articles'),
    url(r'^write/$', views.write, name='write'),
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^preview/$', views.preview, name='preview'),
    url(r'^drafts/$', views.drafts, name='drafts'),
    url(r'^comment/$', views.comment, name='comment'),
    url(r'^tag/(?P<tag_name>.+)/$', views.tag, name='tag'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='edit_article'),
    url(r'^(?P<slug>[-\w]+)/$', views.article, name='article'),
]