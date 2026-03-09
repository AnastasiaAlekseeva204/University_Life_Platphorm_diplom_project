from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from .models import Event
from .models import Community
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login


def index(request):
    events = Event.objects.all().order_by('-date_time')[:3]
    community = Community.objects.all().order_by('-created_at')[:2]
    return render(request, 'index.html',{'events': events,'community':community})

def events(request):
    all_events = Event.objects.all().order_by('-date_time')
    return render(request,'events.html',{'all_events':all_events})

def event_detail(request,event_id):
    event_det = get_object_or_404(Event,pk = event_id)
    return render(request, 'event_detail.html', {'event_det': event_det})

def communities(request):
    all_communities = Community.objects.all().order_by('-created_at')
    return render(request, 'communities.html', {'all_communities':all_communities})

def community_detail(request,community_id):
    com_det = get_object_or_404(Community,pk = community_id)
    return render(request,'community_detail.html', {'com_det': com_det})

def aboutus(request):
    return render(request,'aboutus.html')

def register(request):
    return render(request,'registration/register.html')

def login(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method=='POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")
        user = authenticate(request,username = username, password = password)
        if user is not None:
            auth_login(request,user)
            if not remember:
                request.session.set_expiry(0)
                messages.success(request,f'Добро пожаловать,{user.username}!')
                return redirect("profile")
            else:
                messages.error(request,'Неверный username или пароль')
                return redirect("login")
    return render(request,'registration/login.html')

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,'Пожалуйста войдите в систему, чтобы посмотреть профиль')
        return redirect("login")
    if request.method=='POST':
        user = request.user
        user.name = request.POST.get('name', '')
        user.last_name_student = request.POST.get('last_name_student', '')
        user.middle_name_student = request.POST.get('middle_name_student', '')
        user.email = request.POST.get('email', '')
        user.about_text = request.POST.get('about_text', '')
        user.birth_date = request.POST.get('birth_date', '')
        if request.FILES.get('img'):
            user.img = request.FILES['img']
        
        user.save()
        messages.success(request, 'Профиль успешно обновлен')
        return redirect('profile')
    events = Event.objects.all()
    return render(request,'registration/profile.html',{'events':events})

#def logout(request):
#    return render(request, 'registration/logout.html')
