from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('events',views.events,name='events'),
    path('communities',views.communities, name='communities'),
    path('aboutus', views.aboutus,name='aboutus'),
    path('communities/<int:community_id>/', views.community_detail, name='community_detail'),
    path('events/<int:event_id>/',views.event_detail, name='event_detail'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('profile',views.profile,name='profile'),
    #path('logout',views.logout,name='logout'),
    path('logout', auth_views.LogoutView.as_view(template_name='registration/logout.html',next_page='index'),  name='logout'),
    path('event/<int:event_id>/join/',views.join_event, name='join_event'),
    path('community/<int:community_id>/join/',views.join_community, name='join_community'),
    path('community/<int:community_id>/delete/',views.delete_community,name='delete_community'),
    path('event/<int:event_id>/delete/',views.delete_event,name='delete_event'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('resetpassword/<str:username>/',views.resetpassword,name='resetpassword'),
    path('activeratingpoints',views.activeratingpoints,name='activeratingpoints'),
]