from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q

from blog.models import Post
from blog.time_ago import time_ago
import datetime
import pytz

from .forms import AccountRegisterForm, AccountAuthenticationForm, SetPasswordForm, UserUpdateForm, PasswordResetForm
from .tokens import account_activation_token

# Create your views here.

def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('account:signin')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('blog:home')

def activate_email(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('email_message.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user.username}</b>, please check your email <b>{to_email}</b> inbox and click on \
                    received link to confirm and complete the registration. <b>Note:</b> check you spam folder.', extra_tags='safe')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed correctly.')

def signup(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect('blog:home')

    if request.POST:
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            activate_email(request, user, form.cleaned_data.get('email').lower())
            destination = kwargs.get('next')
            if destination:
                return redirect(destination)
            return redirect('blog:home')
            #email = form.cleaned_data['email'].lower()
            #raw_pass = form.cleaned_data['password1']
            #account = authenticate(email=email, password = raw_pass)
            #login(request, account)
        else:
            context['registration_form'] = form
            for error in list(form.errors.values()):
                messages.error(request, error)
    
    return render(request, 'signup.html', context)

@login_required
def signout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('blog:home')

def signin(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect('blog:home')
    
    destination = get_redirect_if_exists(request)
    print(f"destination {str(destination)}")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            
            if user:
                login(request, user)
                if destination:
                    return redirect(destination)
                return redirect('blog:home')
        else:
            context['login_form'] = form
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = AccountAuthenticationForm()

    return render(request, "signin.html", context)

@login_required
def password_change(request, username):
    user = request.user
    if request.POST:
        form = SetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password changed!")
            return redirect('account:signin')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    
    form = SetPasswordForm(user)
    return render(request, "password_change.html", {'form': form})

def password_reset(request):
    if request.POST:
        form = PasswordResetForm(request.POST)
        print(form)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_model().objects.filter(Q(email=email)).first()
            try:
                if user.is_active:
                    subject = 'Password reset'
                    message = render_to_string('email_password_reset.html', {
                        'user': user,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http'
                        })
                    email_message = EmailMessage(subject, message, to=[user.email])
                    if email_message.send():
                        messages.success(request,
                                        """
                                        <h2>Password reset sent</h2>
                                        <p>
                                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                                            you registered with, and check your spam folder.
                                        </p>
                                        """,
                                        extra_tags='safe'
                                        )
                    else:
                        messages.error(request, 'Problem sending reset password email, <b>SERVER PROBLEM</b>', extra_tags='safe')
                else:
                    messages.error(request, 'You need validate your email!')
                return redirect('blog:home')
            except:
                messages.error(request, 'Enter a valid email address!')
        
        else:
            for error in list(form.errors.values()):
                    messages.error(request, error)

    form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and account_activation_token.check_token(user, token):
        if request.POST:
            form = SetPasswordForm(user, request.POST)
            print(form)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password reset successfully!')
                return redirect('account:signin')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html')
    else:
        messages.error(request, 'Link is expired')
    
    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect('blog:home')

def profile(request, username):
    now = datetime.datetime.now(pytz.timezone("America/Buenos_Aires"))
    if request.POST:
        user = request.user
        posts, total = get_post(user)
        last = time_ago(now, user.last_login.astimezone(pytz.timezone("America/Buenos_Aires")))
        joined = time_ago(now, user.date_joined.astimezone(pytz.timezone("America/Buenos_Aires")))
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return render(request, 'profile.html', {'user': user, 'posts': posts, 'total': total, 'last':last, 'joined': joined})

        for error in list(form.errors.values()):
            messages.error(request, error)
    
    user = get_user_model().objects.filter(username=username).first()
    posts, total = get_post(user)
    last = time_ago(now, user.last_login.astimezone(pytz.timezone("America/Buenos_Aires")))
    joined = time_ago(now, user.date_joined.astimezone(pytz.timezone("America/Buenos_Aires")))
    return render(request, 'profile.html', {'user': user, 'posts': posts, 'total': total, 'last':last, 'joined': joined})

def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get(next):
            redirect = str(request.GET.get('next'))
    return redirect

def get_post(user):
    dates = []
    posts = Post.objects.filter(author=user).order_by('-date_created')
    total_posts = posts.count()

    now = datetime.datetime.now(pytz.timezone("America/Buenos_Aires"))
    for post in posts:
        date_post = post.date_created
        dates.append(time_ago(now, date_post))

    blogs = zip(posts, dates)
    return blogs, total_posts