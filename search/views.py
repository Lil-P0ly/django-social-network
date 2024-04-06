from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from feeds.models import Feed
from articles.models import Article
from questions.models import Question
from django.contrib.auth.decorators import login_required

@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            return redirect('/search/')
        try:
            search_type = request.GET.get('type')
            if search_type not in ['feed', 'articles', 'questions', 'users']:
                search_type = 'feed'
        except Exception:
            search_type = 'feed'
        
        count = {}
        results = {}

        results['feed'] = Feed.objects.filter(post__iregex=querystring, parent=None)
        results['articles'] = Article.objects.filter(Q(title__iregex=querystring) | Q(content__iregex=querystring))
        results['questions'] = Question.objects.filter(Q(title__iregex=querystring) | Q(description__iregex=querystring))
        results['users'] = User.objects.filter(
            Q(username__iregex=querystring) |
            Q(first_name__iregex=querystring) |
            Q(last_name__iregex=querystring) |
            Q(email__iregex=querystring) |
            Q(profile__job_title__iregex=querystring) |
            Q(profile__url__iregex=querystring) |
            Q(profile__location__iregex=querystring))
        
        count['feed'] = results['feed'].count()
        count['articles'] = results['articles'].count()
        count['questions'] = results['questions'].count()
        count['users'] = results['users'].count()

        return render(request, 'search/results.html', {
            'hide_search': True,
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })
    else:
        return render(request, 'search/search.html', {'hide_search': True})