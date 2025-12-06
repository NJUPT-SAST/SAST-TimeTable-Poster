import time
import json
from lark_oapi.api.calendar.v4 import *

from lark import *
from review import review_schedules
from poster import creat_poster
from utils import Schedule


with open("info.json", "r", encoding="utf-8") as f:
    client_info = json.load(f)
    client_id = client_info.get("client_id")
    client_secret = client_info.get("client_secret")
    calender_id = client_info.get("calender_id")

PORT = 45932    # 重定向地址，用于转发授权码，修改时需要在应用后台添加白名单
redirect_uri = f"http://127.0.0.1:{PORT}"
user_access_token = get_access_token(client_id, client_secret, redirect_uri)    # 用户访问令牌(JWT Token)
ROOM = {
    "omm_f2b7a9f9ba5afa0b96906cf2cb4f1a06": "大学生活动中心-汇客厅(112 - 113)",
    "omm_17a653591966274e91219f66043e1218": "大学生活动中心-101 中区",
}
DEPARTMENT = {
    "软件研发部": ["软件研发部", "软研", "软研部"],
    "多媒体部": ["多媒体部", "多媒体"],
    "电子部": ["电子部", "电子"],
}


def get_range_week():
    UTC8_BIAS = 8 * 60 * 60
    WEEK_BIAS = 3 * 24 * 60 * 60 + UTC8_BIAS
    WEEK_SEC = 7 * 24 * 60 * 60

    now = int(time.time())

    week_start = (now + WEEK_BIAS) // WEEK_SEC * WEEK_SEC - WEEK_BIAS
    week_end = week_start + WEEK_SEC

    return week_start, week_end


def prase_schedules(schedules_data: list[CalendarEvent]):
    schedules: dict[str, list[Schedule]] = {
        "软件研发部": [],
        "多媒体部": [],
        "电子部": [],
        "其他": []
    }
    schedules_data.sort(key=lambda x: int(x.start_time.timestamp))
    for item in schedules_data:
        if item.status == "cancelled":
            continue
        start_time = int(item.start_time.timestamp)
        end_time = int(item.end_time.timestamp)
        title = item.summary
        description = item.description
        location = item.location.name if item.location else "未知地点"
        detail: CalendarEvent = get_event_detail(user_access_token, calender_id, item.event_id).event
        for resource in detail.attendees:
            if resource.type == "resource" and resource.room_id in ROOM:
                location = ROOM[resource.room_id]
                break

        schedule = Schedule(title, start_time, end_time, location, description)

        for dept, aliases in DEPARTMENT.items():
            if title.split()[0] in aliases:
                schedules[dept].append(schedule)
                break
        else:
            schedules["其他"].append(schedule)

    for dept, schs in schedules.items():
        lark.logger.debug(f"{'=' * 10} {dept} {'=' * 10}")
        for sch in schs:
            lark.logger.debug(sch.title)
            lark.logger.debug(f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(sch.start_time))} - {time.strftime('%H:%M', time.localtime(sch.end_time))} | {sch.location}")
            lark.logger.debug("\n")

    del schedules["其他"]
    return schedules


def output_posters(schedules: dict[str, list[Schedule]]):
    for dept, schs in schedules.items():
        if schs:
            creat_poster(dept, schs)
            lark.logger.info(f"Poster for {dept:5s} created with {len(schs)} schedules. In output/{dept}.png")
        else:
            lark.logger.info(f"No schedules for {dept}, poster not created.")


if __name__ == "__main__":
    schedules_data = get_schedules(user_access_token, calender_id, *get_range_week()).items
    schedules = prase_schedules(schedules_data)
    confirmed_schedules = review_schedules(schedules)
    output_posters(confirmed_schedules)
