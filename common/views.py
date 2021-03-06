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
    """验证用户是否登录"""

    def wrap(request, *args, **kwargs):
        try:
            token = Token.objects.get(content=request.headers.get("token"))
        except Token.DoesNotExist:
            return get_res("权限验证失败", "")
        return func(request, *args, **kwargs, user=token.user)

    return wrap


def verify_admin(func):
    """验证管理员权限"""

    def wrap(request, *args, **kwargs):
        try:
            token = Token.objects.get(content=request.headers.get("token"))
            assert token.user.is_admin
        except Token.DoesNotExist:
            return get_res("请登录", "")
        except AssertionError:
            return get_res("非管理员用户", "")
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
        "class": user.m_class.name,
        "is_admin": user.is_admin
    })


@except_error
def get_classes(request):
    res = []
    for c in Class.objects.all():
        res.append(model_to_dict(c))
    return get_res("", res)


@csrf_exempt
@except_error
@token_verify
def modify_score(request, **kwargs):
    method = request.method
    data = json.loads(request.body)
    item_id = data.get("id")
    content = data.get("content")
    # 判断项目id正确性
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return get_res("项目id错误", "")

    # 判断评分的项目和用户是否处于同一讲台
    if item.m_class != kwargs.get("user").m_class:
        return get_res("只能对自己讲台的项目评分!!!", "")

    # POST方法为添加评分信息
    if method == "POST":
        # 判断是够为首次添加评分
        try:
            Score.objects.get(item=item, user=kwargs.get("user"))
            return get_res("该评分已存在，请勿重复添加", "")
        except Score.DoesNotExist:
            pass
        score = Score(item=item, user=kwargs.get("user"), content=content)
        score.save()
        return get_res("", "success")
    # PUT方法为修改信息
    elif method == "PUT":
        # 判断评分是否可修改
        try:
            score = Score.objects.get(item=item, user=kwargs.get("user"))
            if score.modification >= 3:
                return get_res("评分次数已达上限", "")
        except Score.DoesNotExist:
            return get_res("未找到相应评分", "")
        # 修改评分
        score.content = content
        score.modification += 1
        score.save()
        return get_res("", "success")
    else:
        return get_res("请求方法有误", "")


@except_error
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


@except_error
@token_verify
def get_my_score(request, **kwargs):
    user = kwargs.get("user")
    scores = []
    for score in Score.objects.filter(user=user):
        scores.append({
            "itemName": score.item.name,
            "content": score.content,
            "modification": score.modification,
            "logo": score.item.logo,
            "itemId": score.item.id
        })
    return get_res("", scores)


@csrf_exempt
@except_error
@verify_admin
def add_class(request, **kwargs):
    """添加讲台"""
    user = kwargs.get("user")
    method = request.method
    data = json.loads(request.body)
    if method != "POST":
        return get_res("请求方法错误", "")
    name = data.get("name")
    if not name:
        return get_res("讲台名称为空", "")
    try:
        Class.objects.get(name=name)
        return get_res("该讲台已存在", "")
    except Class.DoesNotExist:
        _class = Class(name=name)
        _class.save()
        return get_res("", "success")


@except_error
@verify_admin
def get_scores_by_class(request, **kwargs):
    item_id = request.GET.get("itemId")
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return get_res("项目id错误", "")
    res = []
    for score in Score.objects.filter(item=item):
        res.append({
            "name": score.user.name,
            "stuNum": score.user.stuNum,
            "content": score.content,
        })
    return get_res("", res)


@csrf_exempt
@except_error
@verify_admin
def add_item(request, **kwargs):
    data = json.loads(request.body)
    method = request.method
    if method != "POST":
        return get_res("请求方法错误", "")
    name = data.get("name")
    logo = data.get("logo")
    info = data.get("info")
    class_id = data.get("class")
    # 判断class是否有效
    try:
        _class = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return get_res("讲台错误", "")
    item = Item(name=name, logo=logo, info=info, m_class=_class)
    item.save()
    return get_res("", item.id)


@except_error
@verify_admin
def get_all_item(request, **kwargs):
    items = []
    for item in Item.objects.all():
        items.append({
            "id": item.id,
            "name": item.name,
            "logo": item.logo,
            "info": item.info,
            "class": item.m_class.name
        })
    return get_res("", items)


@csrf_exempt
@except_error
@token_verify
def add_feedback(request, **kwargs):
    method = request.method
    data = json.loads(request.body)
    if method != "POST":
        return get_res("请求方法错误", "")
    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return get_res("标题或正文为空！！", "")
    feedback = FeedBack(title=title, content=content, create_time=int(time.time()), user=kwargs.get("user"))
    feedback.save()
    return get_res("", "success")


@csrf_exempt
@except_error
def modify_userinfo(request, **kwargs):
    data = json.loads(request.body)
    method = request.method
    # 获取请求正文
    code = data.get("code")
    stuNum = data.get("stuNum")
    name = data.get("name")
    class_id = data.get("class")
    try:
        m_class = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return get_res("讲台不存在", "")
    if request.method == "POST":
        openid = get_openid(code)
        # 注册用户
        try:
            User.objects.get(openid=openid)
            return get_res("该用户已注册", "")
        except User.DoesNotExist:
            user = User(openid=openid, stuNum=stuNum, name=name, m_class=m_class)
            user.save()
        return get_res("", {
            "stuNum": user.stuNum,
            "name": user.name,
            "token": get_token(user),
            "class": user.m_class.name,
            "is_admin": user.is_admin
        })
    elif method == "PUT":
        # 验证token
        try:
            token = Token.objects.get(content=request.headers.get("token"))
        except Token.DoesNotExist:
            return get_res("权限验证失败", "")

        user = token.user
        user.name = name
        user.m_class = m_class
        user.stuNum = stuNum
        user.save()
        return get_res("", "success")
    else:
        return get_res("请求方法错误", "")

