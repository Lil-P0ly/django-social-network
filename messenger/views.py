# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from activities.decorators import ajax_required
from django.contrib.auth.models import User
import json
from .models import Message

@login_required
def inbox(request):
    conversations = Message.get_conversations(user=request.user)
    active_conversation = None
    messages = None
    if conversations:
        conversation = conversations[0]
        active_conversation = conversation['user'].username
        messages = Message.objects.filter(user=request.user, conversation=conversation['user'])
        messages.update(is_read=True)
        for conversation in conversations:
            if conversation['user'].username == active_conversation:
                conversation['unread'] = 0
    return render(request, 'messenger/inbox.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })

@login_required
def messages(request, username):
    conversations = Message.get_conversations(user=request.user)
    active_conversation = username
    messages = Message.objects.filter(user=request.user, conversation__username=username)
    messages.update(is_read=True)
    for conversation in conversations:
        if conversation['user'].username == username:
            conversation['unread'] = 0
    return render(request, 'messenger/inbox.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })

@login_required
def new(request):
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to')
        try:
            to_user = User.objects.get(username=to_user_username)
        except Exception:
            try:
                to_user_username = to_user_username[to_user_username.rfind('(')+1:len(to_user_username)-1]
                to_user = User.objects.get(username=to_user_username)
            except Exception:
                return redirect('/messages/new/')
        message = request.POST.get('message')
        if len(message.strip()) == 0:
            return redirect('/messages/new/')
        if from_user != to_user:
            Message.send_message(from_user, to_user, message)
        return redirect(u'/messages/{0}/'.format(to_user_username))
    else:
        conversations = Message.get_conversations(user=request.user)
        return render(request, 'messenger/new.html', {'conversations': conversations})

@login_required
@ajax_required
def delete(request):
    return HttpResponse()

# TODO Реализовать удаление, поместить крестик у сообщений
# Из feeds, удаление записи
# @login_required
# @ajax_required
# def remove(request):
#     try:
#         feed_id = request.POST.get('feed')
#         feed = Feed.objects.get(pk=feed_id)
#         if feed.user == request.user:
#             likes = feed.get_likes()
#             parent = feed.parent
#             for like in likes:
#                 like.delete()
#             feed.delete()
#             if parent:
#                 parent.calculate_comments()
#             return HttpResponse()
#         else:
#             return HttpResponseForbidden()
#     except Exception:
#         return HttpResponseBadRequest()


@login_required
@ajax_required
def send(request):
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to')
        to_user = User.objects.get(username=to_user_username)
        message = request.POST.get('message')
        if len(message.strip()) == 0:
            return HttpResponse()
        if from_user != to_user:
            msg = Message.send_message(from_user, to_user, message)
            return render(request, 'messenger/includes/partial_message.html', {'message': msg})
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@login_required
@ajax_required
def users(request):
    users = User.objects.filter(is_active=True)
    dump = []
    template = u'{0} ({1})'
    for user in users:
        if user.profile.get_screen_name() != user.username:
            dump.append(template.format(user.profile.get_screen_name(), user.username))
        else:
            dump.append(user.username)
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')

@login_required
@ajax_required
def check(request):
    count = Message.objects.filter(user=request.user, is_read=False).count()
    return HttpResponse(count)