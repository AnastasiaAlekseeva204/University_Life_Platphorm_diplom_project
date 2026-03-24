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
    first_image = event.get_first_image()
    new_content = event.clean_first_image()
    return render(request, "events_parser/parsed_event_detail.html", {"event": event, "first_image": first_image, "new_content":new_content})


@login_required(login_url='login')
def join_parsed_event(request, pk):
    event = get_object_or_404(ParsedEvent, pk=pk)
    first_image = event.get_first_image()
    new_content = event.clean_first_image()
    if event.participants.filter(id=request.user.id).exists():
        messages.warning(request, "Вы уже записаны на это мероприятие.")
        return redirect('parsed_event_detail', pk=pk)
    else:
        event.participants.add(request.user)
        messages.success(request,"Вы записаны на мероприятие")
    '''if request.method == 'POST':
        # Логика записи (например, сохранение в базу данных)
        messages.success(request, f'Вы успешно записались на мероприятие "{event.title}"')
        return redirect('parsed_event_detail', pk=pk)'''
    return render(request, "events_parser/parsed_event_detail.html", {"event": event, "first_image": first_image, "new_content":new_content})





