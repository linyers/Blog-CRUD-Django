from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.utils import timezone

from .models import Post
from .forms import PostForm, PostUpdateForm
from .time_ago import time_ago
import datetime
import pytz

# Create your views here.
def home(request):
    dates = []
    total_posts = {}
    posts = Post.objects.all().order_by('-date_created')

    for post in posts:
        now = datetime.datetime.now(pytz.timezone("America/Buenos_Aires"))
        date_post = post.date_created.astimezone(pytz.timezone("America/Buenos_Aires"))
        
        if total_posts.keys() != post.author.id:
            total_posts[post.author.id] = posts.filter(author=post.author).count()
        dates.append(time_ago(now, date_post))

    blogs = zip(posts, dates)

    return render(request, 'home.html', {'blogs': blogs, 'total_posts': total_posts.items()})

def create_post(request):
    if request.POST:
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('blog:home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    
    form = PostForm()
    return render(request, 'post_create.html', {'form': form})

def detail_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    now = datetime.datetime.now(pytz.timezone("America/Buenos_Aires"))
    created = time_ago(now, post.date_created.astimezone(pytz.timezone("America/Buenos_Aires")))

    user = post.author
    last = time_ago(now, user.last_login.astimezone(pytz.timezone("America/Buenos_Aires")))

    if post.date_updated != post.date_created:
        updated = time_ago(now, post.date_updated.astimezone(pytz.timezone("America/Buenos_Aires")))
        return render(request, 'post_detail.html', {'post': post, 'created':created, 'updated':updated, 'last':last})
    return render(request, 'post_detail.html', {'post': post, 'created':created, 'last':last})

def update_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.POST:
        form = PostUpdateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            post.title, post.description= title, description
            post.date_updated = datetime.datetime.utcnow()
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    
    form = PostUpdateForm(post)
    return render(request, 'post_update.html', {'form': form, 'post': post})

def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post delete successfully!')
        return redirect('blog:home')
    else:
        messages.error(request, 'Post delete error!')
        raise Http404()