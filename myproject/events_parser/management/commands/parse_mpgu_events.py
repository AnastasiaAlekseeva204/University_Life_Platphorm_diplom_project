"""
Команда: python manage.py parse_mpgu_events
Парсит анонсы с https://mpgu.su/anonsyi/ и сохраняет в ParsedEvent.
"""
from django.core.management.base import BaseCommand
from events_parser.parser import fetch_listing, parse_date_dot
from events_parser.models import ParsedEvent


class Command(BaseCommand):
    help = "Парсит мероприятия с сайта МПГУ и сохраняет в базу (ParsedEvent)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-detail",
            action="store_true",
            help="Не загружать детальную страницу каждого события (только список)",
        )

    def handle(self, *args, **options):
        fetch_details = not options["no_detail"]
        self.stdout.write("Подключаюсь к МПГУ...")
        events, err = fetch_listing(fetch_details=fetch_details)
        if err:
            self.stdout.write(self.style.ERROR(f"Ошибка запроса: {err}"))
            return
        self.stdout.write(f"Найдено событий: {len(events)}")
        created = updated = 0
        for ev in events:
            #date_at = parse_date_dot(ev["date_str"])
            date_at = ev.get("event_date")
            if not date_at:
                date_at = parse_date_dot(ev["date_str"])
            obj, was_created = ParsedEvent.objects.update_or_create(
                source_url=ev["link"],
                defaults={
                    "title": ev["name"],
                    "date_at": date_at,
                    "excerpt": ev.get("excerpt", ""),
                    "content": ev.get("content_html", ""),
                    "content_plain": ev.get("content_text", ""),
                    "image_url": ev.get("image_url", ""),
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f"  + {ev['name'][:60]}...")
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Готово: создано {created}, обновлено {updated}"))
