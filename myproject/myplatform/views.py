from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from .models import Event
from .models import Community
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    return render(request,'registration/login.html')

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,'Пожалуйста войдите в систему, чтобы посмотреть профиль')
        return redirect("login")
    return render(request,'registration/profile.html')

#def logout(request):
#    return render(request, 'registration/logout.html')
