from django.urls import path

from .views import LoginView, MeCentreView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("me/centre/", MeCentreView.as_view(), name="me-centre"),
]
