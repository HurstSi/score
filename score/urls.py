"""score URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from common.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    # 用户相关
    path("users/auth", login),  # 登录
    path("users/", register),   # 注册

    # 讲台相关
    path("classes", get_classes),   # 获取讲台列表
    path("classes/", add_class),   # 添加讲台

    # 项目相关
    path("item/<item_id>", get_item),   # 获取项目详情
    path("item/", add_item),            # 添加项目
    path("item", get_all_item),         # 获取所有项目

    # 评分相关
    path("score/", modify_score),   # 添加/修改评分
    path("score", get_my_score),    # 获取用户评分列表
    path("score/item", get_scores_by_class),    # 获取项目所有评分

    # 反馈相关
    path("feedbacks/", add_feedback),   # 添加反馈
]
