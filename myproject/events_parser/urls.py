from django.urls import path
from . import views

urlpatterns = [
    path("", views.parsed_event_list, name="parsed_event_list"),
    path("<int:pk>/", views.parsed_event_detail, name="parsed_event_detail"),
]
