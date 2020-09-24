import requests
import json


def get_openid(code):
    data = {
        "appid": "wx4eaafb41b19cef49",
        "secret": "32b54bef67778f1723a487e2d042acbc",
        "js_code": code,
        "grant_type": "authorization_code"
    }

    response = requests.get("https://api.weixin.qq.com/sns/jscode2session", params=data)
    res_data = json.loads(response.text)
    return res_data['openid']