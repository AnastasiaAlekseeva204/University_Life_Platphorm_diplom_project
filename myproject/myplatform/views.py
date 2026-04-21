from pathlib import Path
import re

from django.conf import settings
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from .models import Event
from .models import Community
from .models import Faculty
from .models import User
from events_parser.models import ParsedEvent
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login



def index(request):
    events = Event.objects.all().order_by('-date_time')[:3]
    community = Community.objects.all().order_by('-created_at')[:2]
    events_parsed = ParsedEvent.objects.all().order_by('?')[:3]
    return render(request, 'index.html',{'events': events,'community':community,'events_parsed': events_parsed})

def presentation(request):
    from django.http import HttpResponse
    return HttpResponse("Страница презентации в разработке")

def events(request):
    all_events = Event.objects.all().order_by('-date_time')
    parsed_events = ParsedEvent.objects.all().order_by('-date_at')
    return render(request,'events.html',{'all_events':all_events, 'parsed_events':parsed_events})

def event_detail(request,event_id):
    event_det = get_object_or_404(Event,pk = event_id)
    event_count = event_det.participants.count()
    return render(request, 'event_detail.html', {'event_det': event_det,'event_count': event_count})

@login_required(login_url='login')
def join_event(request,event_id):
    event = get_object_or_404(Event,pk=event_id)
    if event.participants.filter(id=request.user.id).exists():
        messages.warning(request, "Вы уже записались на мероприятие")
    else:
        event.participants.add(request.user)
        messages.success(request,"Вы записаны на мероприятие")
    return render(request,'event_detail.html',{'event_det': event})


def delete_event(request,event_id):
    delete_event = get_object_or_404(Event,pk=event_id)
    if delete_event.participants.filter(id=request.user.id).exists():
        delete_event.participants.remove(request.user)
        messages.success(request,f'Вы отказались от участия в мероприятие "{delete_event.name}"')
    return render(request,"registration/profile.html")

def delete_event_parser(request,event_id):
    delete_event_parser = get_object_or_404(ParsedEvent,pk=event_id)
    if delete_event_parser.participants.filter(id=request.user.id).exists():
        delete_event_parser.participants.remove(request.user)
        messages.success(request,f'Вы отказались от участия в анонсах"{delete_event_parser.title}"')
    return render(request, "registration/profile.html")
def communities(request):
    all_communities = Community.objects.all().order_by('-created_at')
    return render(request, 'communities.html', {'all_communities':all_communities})

def community_detail(request,community_id):
    com_det = get_object_or_404(Community,pk = community_id)
    com_count = com_det.participants.count()
    return render(request,'community_detail.html', {'com_det': com_det,'com_count': com_count})

@login_required(login_url='login')
def join_community(request,community_id):
    community = get_object_or_404(Community,pk=community_id)
    com_count = community.participants.count()
    if community.participants.filter(id=request.user.id).exists():
        messages.warning(request,"Вы участник")
    else:
        community.participants.add(request.user)
        messages.success(request,"Вы присоединились")
    return render(request,'community_detail.html',{'com_det':community, 'com_count':com_count})

def delete_community(request,community_id):
    delete_community = get_object_or_404(Community,pk=community_id)
    if delete_community.participants.filter(id=request.user.id).exists():
        delete_community.participants.remove(request.user)
        messages.success(request,f'Вы вышли из сообщества "{delete_community.name}"')
    return render(request,'registration/profile.html')

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
                #messages.error(request,'Неверный username или пароль')
                return redirect("login")
    return render(request,'registration/login.html')

def forgotpassword(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            return redirect("resetpassword", username=user.username)
        except User.DoesNotExist:
            messages.error(request, 'Нет такого пользователя')
            return redirect("forgotpassword")
        
    return render(request, "registration/forgotpassword.html")

def resetpassword(request, username):
    # Находим пользователя сразу, чтобы выдать 404 если ника нет
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'Ошибка доступа')
        return redirect("forgotpassword")

    if request.method == 'POST':
        new_pass = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_password')

        if new_pass == confirm_pass:
            # Важно: используем set_password для хеширования
            user.set_password(new_pass)
            user.save()
            messages.success(request, 'Пароль успешно изменен! Войдите в аккаунт.')
            return redirect('login')
        else:
            messages.error(request, 'Пароли не совпадают')

    return render(request, "registration/resetpassword.html", {'username': username})

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,'Пожалуйста войдите в систему, чтобы посмотреть профиль')
        return redirect("login")
    user = request.user
    if request.method=='POST':
        user = request.user
        user.name = request.POST.get('name', '')
        user.last_name_student = request.POST.get('last_name_student', '')
        user.middle_name_student = request.POST.get('middle_name_student', '')
        user.email = request.POST.get('email', '')
        user.about_text = request.POST.get('about_text', '')
        user.birth_date = request.POST.get('birth_date', '')
        faculty_id = request.POST.get('faculty')
        if faculty_id:
            user.faculty_id = faculty_id
        else:
            user.faculty = None
        if request.FILES.get('img'):
            user.img = request.FILES['img']
        
        user.save()
        messages.success(request, 'Профиль успешно обновлен')
        return redirect('profile')
    events = Event.objects.all()
    join_events = user.events_joined.all()
    total_rating_event = sum(event.rating for event in join_events)
    faculties = Faculty.objects.all()
    join_communitys = user.communities_joined.all()
    total_rating_community = sum(community.rating for community in join_communitys)
    return render(request,'registration/profile.html',{'events':events, 'faculties': faculties, 'total_rating_event':total_rating_event,'total_rating_community':total_rating_community})



def register(request):
    if request.method == 'POST':
        # Получаем данные
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        first_name = request.POST.get('name')
        last_name = request.POST.get('last_name_student')
        middle_name = request.POST.get('middle_name_student')
        birth_date = request.POST.get('birth_date')
        about = request.POST.get('about_text')
        profile_img = request.FILES.get('img')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Этот никнейм уже занят.")
            return render(request, 'register.html')

        user = User(
            username=username,
            role=role,
            name=first_name,
            last_name_student=last_name,
            middle_name_student=middle_name,
            about_text=about,
            img=profile_img
        )
        
        if birth_date:
            user.birth_date = birth_date
            
        user.set_password(password)
        user.save()

        messages.success(request, "Регистрация прошла успешно! Теперь вы можете войти.")
        return redirect('login')

    return render(request, 'registration/register.html')

def activeratingpoints(request):
    return render(request,'registration/activeratingpoints.html')

#def logout(request):
#    return render(request, 'registration/logout.html')
