from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.http import JsonResponse

def login(request):
    if request.user.is_authenticated:
        return redirect('spots:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('spots:index')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


@login_required
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('spots:index')


def signup(request):
    if request.user.is_authenticated:
        return redirect('spots:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('spots:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)

@login_required
def profile(request, username):
    User = get_user_model()
    person = User.objects.get(username=username)
    context = {
        'person': person,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def delete(request):
    request.user.delete()
    auth_logout(request)
    return redirect('reviews:index')

@login_required
def follow(request, user_pk):
    User = get_user_model()
    you = User.objects.get(pk=user_pk)
    me = request.user

    if you != me:
        if me in you.followers.all():
            you.followers.remove(me)
            is_followed = False
        else:
            you.followers.add(me)
            is_followed = True
        context = {
            'is_followed': is_followed,
            'followings_count': you.followings.count(),
            'followers_count': you.followers.count(),
            'followings': [{'username': f.username, 'pk': f.pk} for f in you.followings.all()],
            'followers': [{'username': f.username,'pk': f.pk} for f in you.followers.all()]
        }
        
        return JsonResponse(context)
    return redirect('accounts:profile', you.username)

def follower(request, user_pk):
    User = get_user_model()
    user = User.objects.get(pk=user_pk)
    followers = [{'username': f.username, 'pk': f.pk} for f in user.followers.all()]
    return JsonResponse({'followers': followers})