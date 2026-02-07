from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('start-interview/', views.start_interview, name='interview'),
    path('interview-chat/', views.interview_chat, name='interview_chat'),
    path('api/interview-chat/', views.interview_chat_api, name='interview_chat_api'),
    path('api/interview-review/', views.interview_review_api, name='interview_review_api'),
    path('interview-review/<int:interview_id>/', views.interview_review, name='interview_review'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('mock-interviews/', views.mock_interviews, name='mock_interviews'),
    # End of URL patterns
]