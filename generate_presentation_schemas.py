from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path("myproject/static/images/presentation")
WIDTH, HEIGHT = 1600, 900
BG = (245, 250, 255)
LINE = (14, 59, 136)
BOX = (230, 240, 255)
TEXT = (11, 30, 67)
ACCENT = (0, 91, 255)


def get_font(size):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = get_font(42)
FONT_TEXT = get_font(24)
FONT_SMALL = get_font(20)


def draw_center_title(draw, title):
    bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    draw.text((x, 28), title, fill=ACCENT, font=FONT_TITLE)


def draw_box(draw, xy, text):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=20, fill=BOX, outline=LINE, width=3)
    lines = text.split("\n")
    line_height = 30
    total_h = line_height * len(lines)
    y = y1 + ((y2 - y1) - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=FONT_TEXT)
        x = x1 + ((x2 - x1) - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=TEXT, font=FONT_TEXT)
        y += line_height


def arrow(draw, start, end):
    draw.line([start, end], fill=LINE, width=4)
    ex, ey = end
    sx, sy = start
    if abs(ex - sx) > abs(ey - sy):
        direction = 1 if ex > sx else -1
        tip = (ex, ey)
        wing1 = (ex - 14 * direction, ey - 8)
        wing2 = (ex - 14 * direction, ey + 8)
    else:
        direction = 1 if ey > sy else -1
        tip = (ex, ey)
        wing1 = (ex - 8, ey - 14 * direction)
        wing2 = (ex + 8, ey - 14 * direction)
    draw.polygon([tip, wing1, wing2], fill=LINE)


def create_architecture():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw_center_title(draw, "Структурная схема приложения")

    boxes = {
        "user": (80, 180, 350, 290),
        "frontend": (430, 180, 760, 290),
        "backend": (840, 180, 1220, 290),
        "models": (590, 380, 1020, 520),
        "db": (590, 620, 1020, 740),
        "parser": (1180, 380, 1530, 520),
        "admin": (80, 380, 430, 520),
        "media": (1060, 620, 1530, 740),
    }
    labels = {
        "user": "Пользователь",
        "frontend": "Frontend\nHTML / Bootstrap",
        "backend": "Backend\nDjango Views",
        "models": "Модели\nUser, Event, Community,\nFaculty, ParsedEvent",
        "db": "База данных\nPostgreSQL",
        "parser": "Парсер\nBeautifulSoup + Requests",
        "admin": "Админка\nDjango",
        "media": "Медиа-хранилище\nИзображения",
    }
    for key, rect in boxes.items():
        draw_box(draw, rect, labels[key])

    arrow(draw, (350, 235), (430, 235))
    arrow(draw, (760, 235), (840, 235))
    arrow(draw, (1030, 290), (960, 380))
    arrow(draw, (805, 520), (805, 620))
    arrow(draw, (1220, 235), (1280, 380))
    arrow(draw, (1180, 450), (1020, 450))
    arrow(draw, (1020, 680), (1060, 680))
    arrow(draw, (840, 235), (430, 450))

    img.save(OUT_DIR / "schema-architecture.png")


def create_db():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw_center_title(draw, "Схема БД со связями")

    entities = {
        "User": (80, 170, 420, 380),
        "Event": (520, 140, 860, 300),
        "Community": (520, 340, 860, 500),
        "Faculty": (520, 560, 860, 760),
        "ParsedEvent": (980, 180, 1520, 620),
    }

    draw_box(draw, entities["User"], "User\nid, username, role,\nemail, faculty_id")
    draw_box(draw, entities["Event"], "Event\nid, name, date_time,\norganizator_id")
    draw_box(draw, entities["Community"], "Community\nid, name, status,\norganizator_id")
    draw_box(draw, entities["Faculty"], "Faculty\nid, name, parent_id")
    draw_box(
        draw,
        entities["ParsedEvent"],
        "ParsedEvent\ntitle, source_url,\ndate_at, excerpt,\ncontent, content_plain,\nimage_url",
    )

    arrow(draw, (420, 230), (520, 210))
    arrow(draw, (420, 290), (520, 420))
    arrow(draw, (420, 350), (520, 630))
    arrow(draw, (860, 210), (980, 280))
    arrow(draw, (860, 420), (980, 380))
    arrow(draw, (860, 640), (980, 500))
    arrow(draw, (700, 760), (700, 560))

    notes = [
        "M2M: User <-> Event (participants)",
        "M2M: User <-> Community (participants)",
        "M2M: User <-> ParsedEvent (participants)",
        "FK: Event.organizator -> User",
        "FK: Community.organizator -> User",
        "FK: User.faculty -> Faculty",
    ]
    y = 790
    for note in notes:
        draw.text((80, y), f"- {note}", fill=TEXT, font=FONT_SMALL)
        y += 24

    img.save(OUT_DIR / "schema-db.png")


def create_parser_flow():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw_center_title(draw, "Блок-схема работы парсера")

    blocks = [
        ("Start Parser", (120, 140, 420, 220)),
        ("Load Main\nAnnouncements Page", (120, 260, 420, 360)),
        ("Successful\nLoad?", (120, 410, 420, 500)),
        ("Parse Event Links", (520, 140, 820, 220)),
        ("For Each Link", (520, 260, 820, 340)),
        ("Load Event Page", (520, 380, 820, 460)),
        ("Successful?", (520, 500, 820, 580)),
        ("Extract Date", (920, 140, 1220, 220)),
        ("Extract Excerpt", (920, 250, 1220, 330)),
        ("Extract HTML\nContent", (920, 360, 1220, 450)),
        ("Find Image URL", (920, 480, 1220, 560)),
        ("Clean and\nFormat Data", (920, 590, 1220, 680)),
        ("Save to\nParsedEvent", (920, 720, 1220, 800)),
        ("More Links?", (1280, 500, 1540, 590)),
        ("End Parser", (1280, 720, 1540, 800)),
        ("Log Error", (120, 560, 420, 640)),
        ("Skip Event", (520, 690, 820, 770)),
    ]
    for text, rect in blocks:
        draw_box(draw, rect, text)

    arrow(draw, (270, 220), (270, 260))
    arrow(draw, (270, 360), (270, 410))
    arrow(draw, (420, 455), (520, 180))
    arrow(draw, (270, 500), (270, 560))
    draw.text((310, 525), "No", fill=TEXT, font=FONT_SMALL)
    draw.text((440, 430), "Yes", fill=TEXT, font=FONT_SMALL)

    arrow(draw, (670, 220), (670, 260))
    arrow(draw, (670, 340), (670, 380))
    arrow(draw, (670, 460), (670, 500))
    arrow(draw, (820, 540), (920, 180))
    arrow(draw, (670, 580), (670, 690))
    draw.text((845, 525), "Yes", fill=TEXT, font=FONT_SMALL)
    draw.text((700, 610), "No", fill=TEXT, font=FONT_SMALL)

    arrow(draw, (1070, 220), (1070, 250))
    arrow(draw, (1070, 330), (1070, 360))
    arrow(draw, (1070, 450), (1070, 480))
    arrow(draw, (1070, 560), (1070, 590))
    arrow(draw, (1070, 680), (1070, 720))
    arrow(draw, (1220, 760), (1280, 560))
    arrow(draw, (1410, 590), (1410, 720))
    arrow(draw, (1280, 540), (820, 300))
    draw.text((1440, 640), "No", fill=TEXT, font=FONT_SMALL)
    draw.text((1160, 435), "Yes", fill=TEXT, font=FONT_SMALL)
    arrow(draw, (420, 600), (1280, 760))
    arrow(draw, (820, 730), (1280, 530))

    img.save(OUT_DIR / "schema-parser-flow.png")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    create_architecture()
    create_db()
    create_parser_flow()
    print("Created diagrams in", OUT_DIR)
