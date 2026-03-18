from django.shortcuts import render, get_object_or_404
from .models import ParsedEvent


def parsed_event_list(request):
    """Список спарсенных мероприятий МПГУ."""
    events = ParsedEvent.objects.all()
    return render(request, "events_parser/parsed_event_list.html", {"events": events})


def parsed_event_detail(request, pk):
    """Детальная страница спарсенного мероприятия."""
    event = get_object_or_404(ParsedEvent, pk=pk)
    return render(request, "events_parser/parsed_event_detail.html", {"event": event})
