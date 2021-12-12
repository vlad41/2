from django.urls import path
from . import views

app_name = 'main'


urlpatterns = [
    # Login
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    # Registration
    path('accounts/register/', views.RegisterUserView.as_view(), name='register'),

    path('accounts/profile/', views.profile_posts, name='profile'),

    # Api token
    path('accounts/profile/personal_token/', views.api_token, name='profile_api_token'),

    path('', views.profile_posts, name='main'),


]

# urlpatterns = [
#     path('', views.index, name='main'),
#     path('current_query', views.current_query, name='query'),
#     path('register', views.register, name='register'),
#     path('login', views.UserLoginView.as_view(), name='login'),
# ]