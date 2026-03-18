from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ParsedEvent


def parsed_event_list(request):
    """Список спарсенных мероприятий МПГУ."""
    events = ParsedEvent.objects.all()
    return render(request, "events_parser/parsed_event_list.html", {"events": events})


def parsed_event_detail(request, pk):
    """Детальная страница спарсенного мероприятия."""
    event = get_object_or_404(ParsedEvent, pk=pk)
    return render(request, "events_parser/parsed_event_detail.html", {"event": event})


@login_required(login_url='login')
def join_parsed_event(request, pk):
    """Запись на спарсенное мероприятие."""
    event = get_object_or_404(ParsedEvent, pk=pk)
    messages.success(request, f'Вы записались на мероприятие "{event.title}"')
    return redirect('events')
