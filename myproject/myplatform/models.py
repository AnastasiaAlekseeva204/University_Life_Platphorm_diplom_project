from django.db import models
from django.contrib.auth.models import AbstractUser
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField
from mptt.fields import TreeForeignKey
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STUDENT = "STUDENT", 'Student'
        ORGANIZER = "ORGANIZER", 'Organizer'
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.ADMIN)
    name = models.CharField(max_length=100,verbose_name="Имя",default='',blank=True)
    last_name_student = models.CharField(max_length=100,verbose_name="Фамилия",default="",blank=True)
    middle_name_student = models.CharField(max_length=100,verbose_name="Отчество",default="",blank=True)
    birth_date = models.DateField(
        verbose_name="Дата рождения",
        blank=True,
        null=True,
        help_text="Формат: ГГГГ-ММ-ДД"
    )
    about_text = models.TextField(verbose_name="О себе",default="",blank=True)
    img = models.ImageField(verbose_name='Фото профиля',upload_to='image/user_image',blank=True,null=True)
    faculty = TreeForeignKey('myplatform.Faculty', on_delete=models.CASCADE, null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.role == 'ADMIN':
            self.is_staff = True
            self.is_superuser = True
        elif self.role == 'STUDENT':
            self.is_staff = False
            self.is_superuser = False
        elif self.role == 'ORGANIZER':
            self.is_staff = True
            self.is_superuser = False
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username}({self.get_role_display()})"
    

class Community(models.Model):
    class Status(models.TextChoices):
        ISACTIVE = "ISACTIVE",'isactive'
        ISNOTACTIVE = "ISNOTACTIVE", 'isnotactive'
        WAIT = "WAIT", 'wait'
    name = models.CharField(max_length=200,verbose_name="Название сообщества")
    description = models.TextField(verbose_name="Описание")
    max_participants = models.PositiveIntegerField(verbose_name="Максимальное количество участников",default=0)
    organizator = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name='communities',
        verbose_name='Организатор',
        limit_choices_to={'role': User.Role.ORGANIZER}
    )
    participants = models.ManyToManyField(
        User,
        related_name='communities_joined',
        blank=True,
        verbose_name="Участники"
    )
    img = models.ImageField(verbose_name='Фото сообщества',upload_to='image/communities',blank=True,null=True)
    status = models.CharField(max_length=50,choices=Status.choices,default=Status.ISNOTACTIVE,verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.PositiveIntegerField(verbose_name="Количество баллов",default=0)
    def __str__(self):
        return f"{self.name}"

class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название мероприятия")
    description = models.TextField(verbose_name="Описание")
    date_time = models.DateTimeField(verbose_name="Дата и время проведения")
    location = models.CharField(max_length=100, verbose_name="Место проведения")
    organizator = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name='events',
        verbose_name='Организатор',
        limit_choices_to={'role': User.Role.ORGANIZER}
    ) 
    participants = models.ManyToManyField(
        User,
        related_name='events_joined',
        blank=True,
        verbose_name="Участники"
    )
    max_participants = models.PositiveIntegerField(verbose_name="Максимальное количество участников")
    img = models.ImageField(verbose_name='Фото мероприятий',upload_to='image/events',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(verbose_name="Количество баллов",default=0)
    def __str__(self):
        return f"{self.name}"
    
    def get_formatted_date(self):
        """Возвращает дату в формате '25 января 2025, 14:30'"""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return f"{self.date_time.day} {months[self.date_time.month]} {self.date_time.year}, {self.date_time.strftime('%H:%M')}"

class Faculty(MPTTModel):
    name = models.CharField(max_length=50,verbose_name='Название факультета')
    description = models.TextField(verbose_name='Описание')
    img = models.ImageField(verbose_name='Фото факультета', upload_to='image/faculties', blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name}"