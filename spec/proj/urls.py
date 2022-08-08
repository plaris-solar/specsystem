"""tests URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include, re_path
from spec.views import CategoryDetail, CategoryList, RoleDetail, RoleList, SpecDetail, SpecList
from user.views import GetUser, AdminToken, UserToken
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('cat/', CategoryList.as_view()),
    # path('cat/<category>', CategoryDetail.as_view()),
    path('category/', CategoryList.as_view()),
    path('category/<cat>', CategoryList.as_view()),
    path('category/<cat>/<sub_cat>', CategoryDetail.as_view()),
    path('role/', RoleList.as_view()),
    path('role/<role>', RoleDetail.as_view()),
    path('spec/', SpecList.as_view()),
    path('spec/<num>', SpecList.as_view()),
    path('spec/<num>/<ver>', SpecDetail.as_view()),

    path('db/qa/delete/', views.QaDbReset.as_view()),
    path('auth/info', GetUser.as_view()),
    path('auth/token/<username>', AdminToken.as_view()),
    path('auth/token', UserToken.as_view()),
    path('env/', views.Env.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^.*$', TemplateView.as_view(template_name="index.html")),
]
