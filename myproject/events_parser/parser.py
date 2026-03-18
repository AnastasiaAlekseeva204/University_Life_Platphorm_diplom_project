"""
Парсер анонсов с сайта МПГУ.
Логика из test_parser_console.py.
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

URL = "https://mpgu.su/anonsyi/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_event_detail(page_url: str, text_max_length: int = 50000):
    """
    Загружает страницу события и извлекает:
    - текст из qwen-markdown-text (excerpt);
    - основной контент (текст);
    - div.content с вложенными секциями в формате HTML;
    - URL изображения.
    Возвращает кортеж (qwen_text, content_text, content_html, image_url).
    """
    try:
        resp = requests.get(page_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        return "", "", "", ""
    soup = BeautifulSoup(resp.text, "html.parser")

    # Извлечение изображения
    image_url = ""
    # Ищем изображение в различных местах
    img_selectors = [
        "img.listing-item-image",
        "img[class*='event']",
        "img[class*='anons']",
        ".rsContent img",
        "article img",
        ".content img",
        "img[src*='upload']",
        "img[src*='image']"
    ]
    for selector in img_selectors:
        img = soup.select_one(selector)
        if img and img.get("src"):
            src = img.get("src")
            if src and not src.endswith(".svg") and "logo" not in src.lower():
                image_url = urljoin(page_url, src)
                break
    
    # Если не нашли, берем первое подходящее изображение
    if not image_url:
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src and not src.endswith(".svg") and "logo" not in src.lower() and "icon" not in src.lower():
                image_url = urljoin(page_url, src)
                break

    qwen_el = soup.select_one("[class*='qwen-markdown-text'], [class*='qwen_markdown_text']")
    if not qwen_el:
        qwen_el = soup.find(class_=re.compile(r"qwen[-_]markdown", re.I))
    qwen_text = ""
    if qwen_el:
        t = qwen_el.get_text(separator=" ", strip=True)
        qwen_text = t[:text_max_length] + ("..." if len(t) > text_max_length else "")

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

    return qwen_text, content_text, content_html, image_url


def parse_date_dot(raw_date: str) -> datetime | None:
    """Парсит дату в формате ДД.ММ.ГГГГ или ДД / ММ / ГГГГ."""
    if not raw_date or raw_date.strip() == "—":
        return None
    raw_date = raw_date.strip().replace(" / ", ".").replace("/", ".")
    parts = [p.strip() for p in raw_date.split(".") if p.strip()]
    if len(parts) >= 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            return datetime(year, month, day, 10, 0)
        except (ValueError, IndexError):
            pass
    return None


def fetch_listing(fetch_details: bool = True):
    """
    Загружает страницу анонсов и возвращает список словарей:
    [{"name", "link", "date_str", "excerpt", "content_text", "content_html", "image_url"}, ...]
    Если fetch_details=True, для каждой карточки подгружается страница события (excerpt, content_*, image_url).
    """
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return [], str(e)

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", class_="listing-item")
    events = []

    if items:
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
                ev = {"name": name, "link": link, "date_str": raw_date}
                if fetch_details and link:
                    qwen_text, content_text, content_html, image_url = fetch_event_detail(link)
                    ev["excerpt"] = qwen_text
                    ev["content_text"] = content_text
                    ev["content_html"] = content_html
                    ev["image_url"] = image_url
                else:
                    ev["excerpt"] = ev["content_text"] = ev["content_html"] = ev["image_url"] = ""
                events.append(ev)
            except Exception:
                continue
        return events, None

    all_links = soup.find_all("a", href=lambda h: h and "/anonsyi/" in h and h != "/anonsyi/")
    seen = set()
    for a in all_links:
        title = (a.get_text(strip=True) or "").strip()
        if not title or len(title) < 5 or title in seen:
            continue
        href = a.get("href") or ""
        if not href or href.endswith("/anonsyi/") or "category" in href or "?" in href:
            continue
        link = urljoin(URL, href)
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
        ev = {"name": title, "link": link, "date_str": date_str}
        if fetch_details and link:
            qwen_text, content_text, content_html, image_url = fetch_event_detail(link)
            ev["excerpt"] = qwen_text
            ev["content_text"] = content_text
            ev["content_html"] = content_html
            ev["image_url"] = image_url
        else:
            ev["excerpt"] = ev["content_text"] = ev["content_html"] = ev["image_url"] = ""
        events.append(ev)

    return events, None
