import json
import time
import logging
import requests
import lark_oapi as lark
from lark_oapi.api.calendar.v4 import *
from lark_oapi.core.const import X_TT_LOGID

import server
import webbrowser
from threading import Thread

lark.logger.setLevel(logging.DEBUG)


def check_token(user_access_token):
    """
    True: token 有效
    False: token 无效
    """
    if user_access_token is None:
        lark.logger.error("User access token is None, please get access token first.")
        return False
    return True


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用

def get_auth_code(client_id, redirect_uri):
    """
    https://open.feishu.cn/document/authentication-management/access-token/obtain-oauth-code
    """
    response_type = "code"
    scope = [
        "calendar:calendar:readonly"
    ]
    # 构建授权 URL
    auth_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?client_id={client_id}&response_type={response_type}&redirect_uri={redirect_uri}&scope={' '.join(scope)}"

    lark.logger.info(f"Opening authorization URL: {auth_url}")

    # 自动在浏览器中打开授权页面
    webbrowser.open(auth_url)
    lark.logger.info("Waiting for authorization...")

    # 本地监听回调地址，获取授权码
    redirect_server = Thread(target=server.run, kwargs={"port": server.PORT}, daemon=True)
    redirect_server.start()
    try:
        auth_code = server.AUTH_CODE.get(timeout=300)
        if auth_code:
            lark.logger.info(f"Authorization code received: {auth_code}")
            return auth_code
        else:
            lark.logger.error("Authorization failed or was denied by the user.")
            exit(-1)
    except:
        lark.logger.error("Authorization timed out.(5min)")
        return None


def get_access_token(client_id, client_secret, redirect_uri):
    """
    https://open.feishu.cn/document/authentication-management/access-token/get-user-access-token
    """
    try:
        with open("token.json", "r") as f:
            token_data = json.load(f)
            obtained_at = token_data.get("obtained_at")
            expires_in = token_data.get("expires_in")
            if int(time.time()) < obtained_at + expires_in - 30:
                user_access_token = token_data.get("access_token")
                lark.logger.info(f"User access token loaded from file: {user_access_token} (expires in {time.strftime('%H:%M:%S', time.gmtime(obtained_at + expires_in - int(time.time())))})")
                return user_access_token
            else:
                lark.logger.info("Token has expired, needing to re-authenticate...")
    except FileNotFoundError:
        lark.logger.info("Token file not found, starting authorization process...")
    except json.JSONDecodeError:
        lark.logger.warning("Token file is corrupted, re-authorizing...")
    except Exception as e:
        lark.logger.warning(f"Failed to load token: {e}, re-authorizing...")

    auth_code = get_auth_code(client_id, redirect_uri)
    if auth_code is None:
        user_access_token = None
        return user_access_token
    url = "https://open.feishu.cn/open-apis/authen/v2/oauth/token"
    headers = {"Content-Type": "application/json"}
    body = {
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, headers=headers, json=body)
    json_response = json.loads(response.content)
    if response.status_code != 200:
        lark.logger.error(f"Get access token failed, code: {json_response['code']}, msg: {json_response['error_description']}, log_id: {response.headers.get(X_TT_LOGID)}, resp: \n{json.dumps(json_response, indent=4, ensure_ascii=False)}")
        return None
    user_access_token = json_response["access_token"]
    expires_in = json_response["expires_in"]
    lark.logger.info(f"User access token received: {user_access_token} (expires in {time.strftime('%H:%M:%S', time.gmtime(expires_in))})")

    with open("token.json", "w") as f:
        token_data = {
            "access_token": user_access_token,
            "expires_in": expires_in,
            "obtained_at": int(time.time()),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        json.dump(token_data, f, indent=4)

    return user_access_token


def get_schedules(user_access_token, calender_id, start_time, end_time):
    """
    https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/list
    """
    if not check_token(user_access_token):
        return

    # 创建client
    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.INFO) \
        .build()

    # 构造请求对象
    request: ListCalendarEventRequest = ListCalendarEventRequest.builder() \
        .calendar_id(calender_id) \
        .page_size(500) \
        .start_time(f"{start_time}") \
        .end_time(f"{end_time}") \
        .build()

    # 发起请求
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    response: ListCalendarEventResponse = client.calendar.v4.calendar_event.list(request, option)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.calendar.v4.calendar_event.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    with open("schedules.json", "w", encoding="utf-8") as f:
        f.write(lark.JSON.marshal(response.data, indent=4))
    # lark.logger.debug(lark.JSON.marshal(response.data, indent=4))
    return response.data


def get_event_detail(user_access_token, calender_id, event_id):
    """
    https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/get
    """
    if not check_token(user_access_token):
        return

        # 创建client
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: GetCalendarEventRequest = GetCalendarEventRequest.builder() \
        .calendar_id(calender_id) \
        .event_id(event_id) \
        .need_meeting_settings(False) \
        .need_attendee(True) \
        .build()

    # 发起请求
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    response: GetCalendarEventResponse = client.calendar.v4.calendar_event.get(request, option)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.calendar.v4.calendar_event.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    # lark.logger.debug(lark.JSON.marshal(response.data, indent=4))
    return response.data
