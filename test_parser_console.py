"""
Тест парсера событий МПГУ — вывод данных в консоль (без Django).
Соответствует логике parser_example.py.
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

URL = "https://mpgu.su/anonsyi/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_event_detail(page_url: str, text_max_length: int = 2000):
    """
    Загружает страницу события и извлекает:
    - текст из qwen-markdown-text;
    - основной контент (текст);
    - div.content с вложенными секциями в формате HTML.
    Возвращает кортеж (qwen_text, content_text, content_html).
    """
    try:
        resp = requests.get(page_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        return "", "", ""
    soup = BeautifulSoup(resp.text, "html.parser")

    # qwen-markdown-text
    qwen_el = soup.select_one("[class*='qwen-markdown-text'], [class*='qwen_markdown_text']")
    if not qwen_el:
        qwen_el = soup.find(class_=re.compile(r"qwen[-_]markdown", re.I))
    qwen_text = ""
    if qwen_el:
        t = qwen_el.get_text(separator=" ", strip=True)
        qwen_text = t[:text_max_length] + ("..." if len(t) > text_max_length else "")

    # Основной контент (текст): на МПГУ — все qwen-markdown-*; иначе — .rsContent, .entry-content
    content_parts = []
    for block in soup.select("[class*='qwen-markdown-paragraph'], [class*='qwen-markdown-text']"):
        content_parts.append(block.get_text(separator=" ", strip=True))
    content_text = ""
    if content_parts:
        content_text = " ".join(content_parts).strip()
        if len(content_text) > 80:
            content_text = content_text[:text_max_length] + ("..." if len(content_text) > text_max_length else "")
    if not content_text:
        content_el = (
            soup.select_one(".rsContent")
            or soup.select_one(".entry-content, .post-content, .article__content, .article-content")
            or soup.select_one("[class*='entry-content'], [class*='post-content']")
            or soup.find(class_=re.compile(r"entry[-_]?content|post[-_]?content", re.I))
        )
        if content_el:
            t = content_el.get_text(separator=" ", strip=True)
            if len(t) > 80:
                content_text = t[:text_max_length] + ("..." if len(t) > text_max_length else "")

    # div.content с вложенными секциями — в формате HTML (без меню: берём колонку с контентом)
    content_html = ""
    content_divs = soup.select("div.content")
    for div in content_divs:
        raw = div.get_text(separator=" ", strip=True)
        if "Навигация по сайту" in raw or ("ПОСТУПЛЕНИЕ" in raw and len(raw) < 1500):
            continue
        inner = "".join(str(c) for c in div.contents)
        if len(inner.strip()) > 100:
            content_html = inner.strip()
            break
    if not content_html:
        rs = soup.select_one(".rsContent")
        if rs:
            content_html = "".join(str(c) for c in rs.contents).strip()

    return qwen_text, content_text, content_html


def parse_date_dot(raw_date: str) -> datetime | None:
    """Парсит дату в формате ДД.ММ.ГГГГ или ДД / ММ / ГГГГ."""
    raw_date = raw_date.strip().replace(" / ", ".").replace("/", ".")
    parts = [p.strip() for p in raw_date.split(".") if p.strip()]
    if len(parts) >= 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            return datetime(year, month, day, 10, 0)
        except (ValueError, IndexError):
            pass
    return None


def main():
    print("Подключаюсь к МПГУ:", URL)
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Ошибка запроса:", e)
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Как в parser_example: карточки с классом listing-item
    items = soup.find_all("div", class_="listing-item")
    if not items:
        # Альтернатива: ищем блоки анонсов по ссылкам и датам
        items = soup.select("article, .post, .annonce-item, .event-item, [class*='listing']")
    if not items:
        # Поиск по структуре: ссылка на /anonsyi/ + дата рядом
        all_links = soup.find_all("a", href=lambda h: h and "/anonsyi/" in h and h != "/anonsyi/")
        seen = set()
        events = []
        for a in all_links:
            title = (a.get_text(strip=True) or "").strip()
            if not title or len(title) < 5 or title in seen:
                continue
            href = a.get("href") or ""
            if not href or href.endswith("/anonsyi/") or "category" in href or "?" in href:
                continue
            link = urljoin(URL, href)
            # Ищем дату в родительском блоке (формат 16 / 03 / 2026)
            parent = a.find_parent(["div", "article", "li", "section"])
            date_str = ""
            if parent:
                text = parent.get_text()
                m = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})", text)
                if m:
                    date_str = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
            if not date_str:
                date_str = "—"
            seen.add(title)
            events.append({"name": title, "link": link, "date_str": date_str})
        if events:
            print("\nНайдено анонсов (по ссылкам):", len(events))
            show_count = min(25, len(events))
            fetch_detail_count = min(5, show_count)  # для первых 5 загружаем qwen-markdown-text и content
            for i, ev in enumerate(events[:show_count], 1):
                dt = parse_date_dot(ev["date_str"]) if ev["date_str"] != "—" else None
                date_out = dt.strftime("%d.%m.%Y") if dt else ev["date_str"]
                print(f"\n--- {i} ---")
                print("Название:", ev["name"])
                print("Ссылка:", ev["link"])
                print("Дата:", date_out)
                if i <= fetch_detail_count:
                    print("Загрузка текста со страницы события...")
                    qwen_text, content_text, content_html = fetch_event_detail(ev["link"])
                    if qwen_text:
                        print("Текст (qwen-markdown-text):", qwen_text)
                    else:
                        print("Текст (qwen-markdown-text): не найден")
                    if content_text:
                        print("Контент (текст):", content_text)
                    else:
                        print("Контент (текст): не найден")
                    if content_html:
                        preview = content_html[:800] + ("..." if len(content_html) > 800 else "")
                        print("Контент (HTML div.content):", preview)
                    else:
                        print("Контент (HTML div.content): не найден")
            if len(events) > show_count:
                print("\n... и ещё", len(events) - show_count, "событий")
            return
        print("Не удалось найти блоки мероприятий (ни listing-item, ни подходящие ссылки).")
        return

    print("\nНайдено карточек (listing-item):", len(items))
    count = 0
    for item in items:
        try:
            title_el = item.find("a", class_="listing-item-title")
            date_el = item.find("div", class_="listing-item-date")
            if not title_el:
                continue
            name = title_el.get_text(strip=True)
            link = title_el.get("href") or ""
            link = urljoin(URL, link) if link else ""
            raw_date = date_el.get_text(strip=True) if date_el else ""
            clean_date = parse_date_dot(raw_date) if raw_date else None
            date_out = clean_date.strftime("%d.%m.%Y %H:%M") if clean_date else raw_date or "—"
            count += 1
            print(f"\n--- {count} ---")
            print("Название:", name)
            print("Ссылка:", link)
            print("Дата:", date_out)
        except Exception as e:
            print("Ошибка элемента:", e)
    print("\nИтого выведено:", count)


if __name__ == "__main__":
    main()
