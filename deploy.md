# Деплой на VPS (без CI/CD)

Домен: **univer.h1n.ru**  
Стек: Django 5.x, Gunicorn, Nginx, systemd. Ручное обновление кода (`git pull` или копирование архива).

Структура репозитория: в корне лежит `manage.py`, каталог приложения Django — `myproject/` (там же `staticfiles/`, `media/`, `db.sqlite3` после миграций).

---

## 1. VPS и DNS

- ОС: Ubuntu 22.04/24.04 LTS (или Debian).
- Открыть в фаерволе: **22** (SSH), **80**, **443**.
- DNS: запись **A** для `univer.h1n.ru` → публичный IP VPS (при IPv6 — **AAAA**).

---

## 2. Пакеты на сервере

Дальше команды рассчитаны на **сессию под root** (`ssh root@…` на VPS или `sudo -i`).

```bash
apt update && apt install -y python3-venv python3-dev build-essential nginx git
```


Код проекта — в **`/home/univer`** (корень репозитория с `manage.py`).

---

## 3. Код на сервер

Создайте каталог на VPS (если его ещё нет):

```bash
mkdir -p /home/univer
```

**Через Git:**

```bash
cd /home/univer
git clone https://github.com/AnastasiaAlekseeva204/University_Life_Platphorm_diplom_project .
```

Каталог `/home/univer` должен быть пустым (кроме скрытых служебных файлов), иначе клонируйте во временную папку и перенесите содержимое в `/home/univer`.

---

## 4. Виртуальное окружение и зависимости

```bash
cd /home/univer
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

---

## 5. Настройки Django для продакшена

Перед публикацией в `myproject/myproject/settings.py` (или через переменные окружения / отдельный модуль настроек):

| Параметр | Рекомендация |
|----------|----------------|
| `SECRET_KEY` | Новый случайный ключ, не хранить в открытом репозитории |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `'univer.h1n.ru'`, при необходимости IP сервера |

База по умолчанию — SQLite (`myproject/db.sqlite3`). Процесс Gunicorn должен иметь права на чтение/запись этого файла и каталога `myproject/`.

Миграции и статика (из **корня** репозитория, где `manage.py`):

```bash
cd /home/univer
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # по желанию
```

Статика собирается в `myproject/staticfiles/`, медиа — `myproject/media/` (см. `STATIC_ROOT` / `MEDIA_ROOT` в `settings.py`).

---

## 6. Gunicorn и systemd

Gunicorn слушает **только localhost** `127.0.0.1:8001` — Nginx проксирует на этот порт. Так не нужно настраивать права на Unix-сокет для пользователя `www-data`.

Файл `/etc/systemd/system/gunicorn-univer.service`:

```ini
[Unit]
Description=Gunicorn (univer Django)
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/univer/myproject
Environment="PATH=/home/univer/.venv/bin"
ExecStart=/home/univer/.venv/bin/gunicorn \
  --workers 3 \
  --bind 127.0.0.1:8001 \
  myproject.wsgi:application

Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`WorkingDirectory` — каталог `myproject/` в репозитории (тот же, что добавляется в `sys.path` из `manage.py`), чтобы модуль `myproject.wsgi` находился корректно.

```bash
systemctl daemon-reload
systemctl enable gunicorn-univer
systemctl start gunicorn-univer
systemctl status gunicorn-univer
```

Логи: `journalctl -u gunicorn-univer -f`.

---

## 7. Nginx

`/etc/nginx/sites-available/univer`:

```nginx
server {
    listen 80;
    server_name univer.h1n.ru;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/univer/myproject/staticfiles/;
    }

    location /media/ {
        alias /home/univer/myproject/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Включение и проверка:

```bash
ln -sf /etc/nginx/sites-available/univer /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## 8. HTTPS (Let’s Encrypt)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d univer.h1n.ru
```

Certbot обновит конфиг Nginx на редирект и TLS.

---

## 9. Ручной деплой после изменений в коде

На VPS:

```bash
cd /home/univer
git pull   # или залить новые файлы вручную
source .venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
deactivate
systemctl restart gunicorn-univer
```

Если менялись только шаблоны/статика вне `collectstatic` — перезапуск Gunicorn всё равно не помешает.

---

## 10. Быстрая проверка

- `curl -I http://127.0.0.1` с сервера после настройки Nginx (или с хоста по домену).
- Админка: `https://univer.h1n.ru/admin/`.
- `python manage.py check --deploy` на сервере с продакшен-настройками.

---

## Примечания

- Запуск приложения от **root** удобен для учебного VPS, но для публичного сервиса безопаснее отдельный системный пользователь и права на файлы.
- Текущий репозиторий может содержать небезопасный `SECRET_KEY` и `DEBUG = True` — для VPS это нужно исправить до выхода в интернет.
- SQLite подходит для небольшой нагрузки на одном сервере; при росте — PostgreSQL и отдельная настройка `DATABASES`.
- После обновления Python-кода без перезапуска Gunicorn воркеры продолжают отдавать старую версию приложения.
