# -*- coding: utf-8 -*-
import os, json
from PIL import Image

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings as django_settings
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import TruncDay
from django.db.models import Count, Q
from django.template import RequestContext


from core.forms import ProfileForm, ChangePasswordForm
from feeds.models import Feed
from feeds.views import FEEDS_NUM_PAGES, feeds
from articles.models import Article, ArticleComment
from questions.models import Question, Answer
from activities.models import Activity


def home(request):
    if request.user.is_authenticated:
        return feeds(request)
    else:
        return redirect('login')

@login_required
def network(request):
    users_list = User.objects.filter(is_active=True).order_by('username')
    paginator = Paginator(users_list, 100)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'core/network.html', { 'users': users })

@method_decorator([login_required], name='dispatch')
class UserList(ListView):
    # model = get_user_model()
    paginate_by = 36
    template_name = 'core/users.html'
    context_object_name = 'users'

    def get_queryset(self):
        query = self.request.GET.get('q','')
        queryset = User.objects.filter(is_active=True).order_by('username')
        if query:
            queryset = queryset.filter(
                Q(username__iregex=query) |
                Q(first_name__iregex=query) |
                Q(last_name__iregex=query) |
                Q(email__iregex=query) |
                Q(profile__job_title__iregex=query) |
                Q(profile__url__iregex=query) |
                Q(profile__location__iregex=query)
            )
        return queryset


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    all_feeds = Feed.get_feeds().filter(user=user)
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    feeds = paginator.page(1)

    counts = {
        'feeds': Feed.objects.filter(user=user).count(),
        'article':Article.objects.filter(create_user=user).count(),
        'article_comment': ArticleComment.objects.filter(user=user).count(),
        'question':Question.objects.filter(user=user).count(),
        'answer':Answer.objects.filter(user=user).count(),
        'activity':Activity.objects.filter(user=user).count(),
        # 'messages':Message.objects.filter(Q(from_user=user) | Q(user=user)).count(),
    }

    # Daily user activity
    user_activity = Activity.objects.filter(user=user).annotate(day=TruncDay(
            'date')).values('day').annotate(c=Count('id')).values('day', 'c')
    dates, datapoints = zip(*[[a['c'], str(a['day'].date())] for a in user_activity]) if user_activity else ([],[])
    data = {
        'page_user': user,
        'counts': counts,
        'global_interactions': sum(counts.values()),  # noqa: E501
        'bar_data': list(counts.values()),
        'line_labels': json.dumps(datapoints),
        'line_data': json.dumps(dates),
        'feeds': feeds,
        'from_feed': feeds[0].id if feeds else -1  # pragma: no cover
    }
    return render(request, 'core/profile.html', data)


@login_required
def settings(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.profile.job_title = form.cleaned_data.get('job_title')
            user.email = form.cleaned_data.get('email')
            user.profile.url = form.cleaned_data.get('url')
            user.profile.location = form.cleaned_data.get('location')
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Ваш профиль успешно изменен.')
    else:
        form = ProfileForm(instance=user, initial={
            'job_title': user.profile.job_title,
            'url': user.profile.url,
            'location': user.profile.location
            })
    return render(request, 'core/settings.html', {'form':form})


# @login_required
def picture(request):
    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True
    except Exception:
        pass
    return render(request, 'core/picture.html', {'uploaded_picture': uploaded_picture})

@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Ваш пароль был успешно изменен')
    else:
        form = ChangePasswordForm(instance=user)
    return render(request, 'core/password.html', {'form':form})

@login_required
def upload_picture(request):
    try:
        if not os.path.exists(str(django_settings.FILE_UPLOAD_TEMP_DIR)):
            os.makedirs(str(django_settings.FILE_UPLOAD_TEMP_DIR))
        if not os.path.exists(str(django_settings.MEDIA_ROOT)):
            os.makedirs(str(django_settings.MEDIA_ROOT))
        profile_pictures = str(django_settings.MEDIA_ROOT) + '/profile_pictures/'
        if not os.path.exists(profile_pictures):
            os.makedirs(profile_pictures)
        f = request.FILES['picture']
        filename = profile_pictures + request.user.username + '_tmp.jpg'
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        im = Image.open(filename)
        im = im.convert("RGB")
        width, height = im.size
        if width > 350:
            new_width = 350
            new_height = int((height * 350) / width)
            new_size = new_width, new_height
            im.thumbnail(new_size)
            im.save(filename)
        # return redirect('/settings/upload_picture=uploaded')  # Выдает ошибку, так что переходим напрямую
        return render(request, 'core/picture.html', {'uploaded_picture': True})
    except Exception as ex:
        return redirect(f'/settings/picture/{ex}')

@login_required
def save_uploaded_picture(request):
    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        w = int(request.POST.get('w'))
        h = int(request.POST.get('h'))
        tmp_filename = str(django_settings.MEDIA_ROOT) + '/profile_pictures/' + str(request.user.username) + '_tmp.jpg'
        filename = str(django_settings.MEDIA_ROOT) + '/profile_pictures/' + str(request.user.username) + '.jpg'
        if os.path.exists(filename):
            os.remove(filename)
        im = Image.open(tmp_filename)
        cropped_im = im.crop((x, y, w+x, h+y))
        cropped_im.thumbnail((200, 200))
        cropped_im.save(filename)
        os.remove(tmp_filename)
    except Exception as ex:
        # return redirect(f'/settings/picture/{ex}')
        pass
    return redirect('/settings/picture/')