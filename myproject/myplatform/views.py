from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from .models import Event
from .models import Community
from .models import Faculty
from .models import User
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

def communities(request):
    all_communities = Community.objects.all().order_by('-created_at')
    return render(request, 'communities.html', {'all_communities':all_communities})

def community_detail(request,community_id):
    com_det = get_object_or_404(Community,pk = community_id)
    return render(request,'community_detail.html', {'com_det': com_det})

def join_community(request,community_id):
    community = get_object_or_404(Community,pk=community_id)
    if community.participants.filter(id=request.user.id).exists():
        messages.warning(request,"Вы участник")
    else:
        community.participants.add(request.user)
        messages.success(request,"Вы присоединились")
    return render(request,'community_detail.html',{'com_det':community})

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
                messages.error(request,'Неверный username или пароль')
                return redirect("login")
    return render(request,'registration/login.html')

def forgotpassword(request):
    if request.method=='POST':
        username=request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            return redirect("resetpassword", username=user.username)
        except User.DoesNotExist:
            messages.error(request,'Нет такого пользователя')
            return redirect("forgotpassword")
        
    return render(request,"registration/forgotpassword.html")

def resetpassword(request,username):
    return render(request,"registration/resetpassword.html",{'username':username})

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
    faculties = Faculty.objects.all()
    return render(request,'registration/profile.html',{'events':events, 'faculties': faculties})

#def logout(request):
#    return render(request, 'registration/logout.html')
