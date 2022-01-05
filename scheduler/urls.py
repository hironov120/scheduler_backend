"""scheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers

from .views import UserViewSet, TaskViewSet, NoteViewSet

router = routers.SimpleRouter()
router.register(r'users', viewset = UserViewSet, basename='user') # (basenameは、ViewSetの中で明示的にget_querysetをオーバーライドしているため記述必須。要はモデル名を指定してる)
router.register(r'tasks', viewset = TaskViewSet, basename='task') 
router.register(r'notes', viewset = NoteViewSet, basename='note') 


print ('SERVERUP')

# ちゃんとしたアプリだと、管理者画面が一つとアプリが複数あるので、adminはここに書かない（管理用のアプリが一個立ってそこに書かれる）
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
]