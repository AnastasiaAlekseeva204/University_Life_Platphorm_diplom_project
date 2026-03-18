from django.urls import path
from . import views

urlpatterns = [
    path("", views.parsed_event_list, name="parsed_event_list"),
    path("<int:pk>/", views.parsed_event_detail, name="parsed_event_detail"),
    path("<int:pk>/join/", views.join_parsed_event, name="join_parsed_event"),
]
