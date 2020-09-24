from django.shortcuts import render
from django.http import JsonResponse
from .utils import *
from .models import *
from django.forms.models import model_to_dict


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
    return get_res("", model_to_dict(user))
