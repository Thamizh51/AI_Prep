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
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('help-center/', views.help_center, name='help_center'),
    path('guides/', views.guides, name='guides'),
    # End of URL patterns
]