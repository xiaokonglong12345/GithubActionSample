import os
import requests
import json
import requests
from datetime import datetime, timedelta

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID列表即 用户列表中的微信号
openIds = os.environ.get("OPEN_IDS").split(",")  # 将多个OPEN_ID用逗号分隔
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")
locations = os.environ.get("LOCATIONS").split(";")
key = os.environ.get("KEY")
def get_weather(location):
    url = 'https://devapi.qweather.com/v7/grid-weather/24h'
    params = {
        'location': location,
        'key': key
    }

    response = requests.get(url, params=params).json()['hourly']
    slow = 0
    fast = 1
    weather_data = {}
    while fast <= 23:
        if response[slow]['text'] != response[fast]['text']:
            # 将时间字符串转换为datetime对象
            time_obj = datetime.strptime(response[slow]['fxTime'][11:16], '%H:%M')
            # 加上8小时
            new_time_obj = time_obj + timedelta(hours=8)
            # 将新的时间转换为字符串，并格式化为24小时制
            new_time_str = new_time_obj.strftime('%H:%M')
            weather_data[new_time_str] = response[slow]['text'] + '-' + response[slow]['temp'] + '℃-' + response[slow][
                'windScale'] + "级-" + response[slow]['humidity'] + '%'
            slow = fast
        fast += 1

    # 打印响应结果
    # 将字典的键值对转换为字符串组成的列表
    weather_data = [f"{key}: {value}" for key, value in weather_data.items()]

    # 检查列表长度
    if len(weather_data) > 5:
        # 如果列表长度超过5，取前五个
        weather_data = weather_data[:5]
    elif len(weather_data) < 5:
        # 如果列表长度不足5，用空字符串填充
        weather_data.extend([''] * (5 - len(weather_data)))
    return weather_data


def get_access_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


def get_daily_love():
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love


def send_weather(access_token, openId, weather):
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")

    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {
                "value": today_str
            },
            "weather0" : {
                "value" : weather[0]
            },
            "weather1": {
                "value": weather[1]
            },
            "weather2": {
                "value": weather[2]
            },
            "weather3": {
                "value": weather[3]
            },
            "weather4": {
                "value": weather[4]
            },
            "today_note": {
                "value": get_daily_love()
            }
        }
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)


def weather_report(this_city,num):
    access_token = get_access_token()
    weather = get_weather(this_city)
    print(f"天气信息： {weather}")
    send_weather(access_token, openIds[num], weather)


if __name__ == '__main__':
    for i in range(len(locations)):
        weather_report(locations[i],i)
