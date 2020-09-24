from django.shortcuts import render
from django.http import JsonResponse
from .utils import *
from .models import *
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from hashlib import md5
import time
import json


def get_token(user):
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        res = md5((user.openid + user.name + str(time.time())).encode())
        token = Token(user=user, content=res.hexdigest(), createTime=int(time.time()))
        token.save()
    return token.content


def get_res(mes, data):
    return JsonResponse({"mes": mes, "data": data})


def except_error(func):
    def wrap(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            return get_res("未知错误", "")

    return wrap


@except_error
def login(request):
    code = request.GET.get("code")
    if not code:
        return get_res("参数错误", "")
    # 获取用户的openid
    openid = get_openid(code)
    try:
        user = User.objects.get(openid=openid)  # 从数据库中获取用户
    except User.DoesNotExist:  # 用户不存在
        return get_res("null", "")
    return get_res("", {
        "stuNum": user.stuNum,
        "name": user.name,
        "token": get_token(user)
    })


@csrf_exempt
def register(request):
    data = json.loads(request.body)
    if request.method != "POST":
        return get_res("请求方法错误", "")
    code = data.get("code")
    stuNum = data.get("stuNum")
    name = data.get("name")
    # 注册用户
    try:
        User.objects.get(name=name)
        return get_res("该用户已注册", "")
    except User.DoesNotExist:
        openid = get_openid(code)
        user = User(openid=openid, stuNum=stuNum, name=name)
        user.save()
    return get_res("", {
        "stuNum": user.stuNum,
        "name": user.name,
        "token": get_token(user)
    })

