from django.urls import path
from .views import signin, signup, activate, profile, signout, password_reset, password_change, password_reset_confirm
app_name = 'account'

urlpatterns = [
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('logout/', signout, name='signout'),
    path('<str:username>/', profile, name='profile'),
    path('<str:username>/password_change/', password_change, name='password_change'),
    path('signin/password_reset/', password_reset, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
]