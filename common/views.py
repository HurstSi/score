from django.shortcuts import render
from django.http import JsonResponse
from .utils import *
from .models import *
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from hashlib import md5
import time
import json


def token_verify(func):
    def wrap(request, *args, **kwargs):
        try:
            token = Token.objects.get(content=request.headers.get("token"))
        except Token.DoesNotExist:
            return get_res("权限验证失败", "")
        return func(request, *args, **kwargs, user=token.user)
    return wrap


def get_token(user):
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        res = md5((user.openid + user.name + str(time.time())).encode())
        token = Token(user=user, content=res.hexdigest(), createTime=int(time.time()))
        token.save()
    return token.content


def get_res(mes, data):
    res = JsonResponse({"mes": mes, "data": data})
    if mes:
        res.status_code = 400
    return res


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
        "token": get_token(user),
        "class": user.m_class.name
    })


@csrf_exempt
def register(request):
    data = json.loads(request.body)
    if request.method != "POST":
        return get_res("请求方法错误", "")
    code = data.get("code")
    stuNum = data.get("stuNum")
    name = data.get("name")
    class_id = data.get("class")
    try:
        m_class = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return get_res("讲台不存在", "")
    # 注册用户
    try:
        User.objects.get(name=name)
        return get_res("该用户已注册", "")
    except User.DoesNotExist:
        openid = get_openid(code)
        user = User(openid=openid, stuNum=stuNum, name=name, m_class=m_class)
        user.save()
    return get_res("", {
        "stuNum": user.stuNum,
        "name": user.name,
        "token": get_token(user),
        "class": user.m_class.name
    })


def get_classes(request):
    res = []
    for c in Class.objects.all():
        res.append(model_to_dict(c))
    return get_res("", res)


@token_verify
def get_item(request, item_id, **kwargs):
    try:
        item = Item.objects.get(id=int(item_id))
    except Item.DoesNotExist:
        return get_res("id有误", "")
    return get_res("", {
        "name": item.name,
        "logo": item.logo,
        "info": item.info,
        "class": item.m_class.name
    })
