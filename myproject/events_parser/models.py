from django.db import models
from ckeditor.fields import RichTextField
from bs4 import BeautifulSoup
from myplatform.models import User

class ParsedEvent(models.Model):
    """Событие, спарсенное с сайта МПГУ."""
    title = models.CharField("Название", max_length=500)
    source_url = models.URLField("Ссылка на источник", unique=True)
    date_at = models.DateTimeField("Дата мероприятия", null=True, blank=True)
    excerpt = models.TextField("Краткое описание (qwen-markdown)", blank=True)
    content = RichTextField("Текст (HTML)", blank=True)
    content_plain = models.TextField("Текст (plain)", blank=True)
    image_url = models.URLField("URL изображения", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField(   
        User,
        related_name='parsed_event_joined',
        blank=True,
        verbose_name="Участники"
    )
    
    def get_first_image(self):
       soup = BeautifulSoup(self.content, features="html.parser")
       first_img = soup.find('img')
       if first_img:
           return first_img['src']
       return ""
    
    def clean_first_image(self):
        soup = BeautifulSoup(self.content, features="html.parser")
        first_img = soup.find('img')
        if first_img:
            first_img.decompose()
        return str(soup)

    class Meta:
        verbose_name = "Спарсенное мероприятие"
        verbose_name_plural = "Спарсенные мероприятия"
        ordering = ["-date_at", "-created_at"]

    def __str__(self):
        return self.title
