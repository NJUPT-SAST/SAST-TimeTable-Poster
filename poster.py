from PIL import Image, ImageDraw, ImageFont
import time

from utils import Schedule


logo_path = f"assets/SAST-logo.png"
logo = Image.open(logo_path).convert("RGBA")
logo_w, logo_h = logo.size
percent = 0.4
logo = logo.resize((int(logo_w * percent), int(logo_h * percent)))
华文琥珀 = ImageFont.truetype("fonts/华文琥珀.ttf", 100)
思源黑体 = ImageFont.truetype("fonts/SourceHanSansSC-Regular.otf", 80)
思源宋体 = ImageFont.truetype("fonts/SourceHanSerifSC-Regular.otf", 80)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR = {
    "软件研发部": (40, 40, 40),
    "多媒体部": (74, 51, 129),
    "电子部": (82, 122, 141),
}
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
BLOCK_HEIGHT = 570


def draw_textblock(draw: ImageDraw.ImageDraw, color, position: tuple[int, int], sch: Schedule, index: int):
    date = time.strftime("%Y-%m-%d", time.localtime(sch.start_time))
    week = WEEKDAYS[time.localtime(sch.start_time).tm_wday]
    start_time = time.strftime("%H:%M", time.localtime(sch.start_time))
    end_time = time.strftime("%H:%M", time.localtime(sch.end_time))

    tmp = sch.title.split()
    group, context = tmp[1], " ".join(tmp[2:])

    title_position = (position[0], position[1])
    context_position = (position[0] + 10, position[1] + 160)
    time_position = (position[0] + 10, position[1] + 280)
    location_position = (position[0] + 10, position[1] + 400)

    # title background
    bbox = draw.textbbox(title_position, f"{index}. {group}", font=华文琥珀)
    draw.rectangle([(bbox[0], bbox[1]), (bbox[2], bbox[3])], fill=color)
    draw.rectangle([(bbox[0] - 30, bbox[1]), (bbox[0], bbox[3])], fill=color)
    draw.rectangle([(bbox[0], bbox[1] - 30), (bbox[2], bbox[1])], fill=color)
    draw.rectangle([(bbox[0], bbox[3]), (bbox[2], bbox[3] + 30)], fill=color)
    draw.rectangle([(bbox[2], bbox[1]), (bbox[2] + 30, bbox[3])], fill=color)
    draw.ellipse([(bbox[0] - 30, bbox[1] - 30), (bbox[0] + 30, bbox[1] + 30)], fill=color)
    draw.ellipse([(bbox[0] - 30, bbox[3] - 30), (bbox[0] + 30, bbox[3] + 30)], fill=color)
    draw.ellipse([(bbox[2] - 30, bbox[1] - 30), (bbox[2] + 30, bbox[1] + 30)], fill=color)
    draw.ellipse([(bbox[2] - 30, bbox[3] - 30), (bbox[2] + 30, bbox[3] + 30)], fill=color)

    draw.text(title_position, f"{index}. {group}", font=华文琥珀, fill=WHITE)
    draw.text(context_position, f"授课内容：{context}", font=思源黑体, fill=BLACK)
    draw.text(time_position, f"时间：{date} ({week}) {start_time} - {end_time}", font=思源黑体, fill=BLACK)
    draw.text(location_position, f"地点：{sch.location}", font=思源黑体, fill=BLACK)


def creat_poster(dept: str, schs: list[Schedule]):
    assert len(schs) <= 8, ValueError("Too many schedules to fit in the poster.")

    background_path = f"assets/{dept}.png"
    output_path = f"output/{dept}.png"

    pic = Image.open(background_path).convert("RGB")
    w, h = pic.size
    pos_w = 160
    pos_h = 620

    draw = ImageDraw.Draw(pic)

    for n, sch in enumerate(schs, 1):
        draw_textblock(draw, COLOR[dept], (pos_w, pos_h), sch, n)
        pos_h += BLOCK_HEIGHT

    pic.paste(logo, (pos_w, pos_h), mask=logo.split()[-1])
    pos_h += logo_h * percent + 40

    assert pos_h <= h, "Poster height exceeded."

    pic = pic.crop((0, 0, w, pos_h))
    pic.save(output_path)


if __name__ == "__main__":
    schs = [
        Schedule(
            "软件研发部 Python组 第一次授课",
            int(time.time() + 86400),
            int(time.time() + 86400 + 7200),
            "大学生活动中心-101",
            "Python基础入门课程"
        ),
        Schedule(
            "软件研发部 后端组 Springboot入门",
            int(time.time() + 86400 * 2),
            int(time.time() + 86400 * 2 + 7200),
            "大学生活动中心-113",
            "学习Spring框架"
        ),
        Schedule(
            "软件研发部 Python组 第一次授课",
            int(time.time() + 86400),
            int(time.time() + 86400 + 7200),
            "大学生活动中心-101",
            "Python基础入门课程"
        ),
        Schedule(
            "软件研发部 后端组 Springboot入门",
            int(time.time() + 86400 * 2),
            int(time.time() + 86400 * 2 + 7200),
            "大学生活动中心-113",
            "学习Spring框架"
        ),
        Schedule(
            "软件研发部 Python组 第一次授课",
            int(time.time() + 86400),
            int(time.time() + 86400 + 7200),
            "大学生活动中心-101",
            "Python基础入门课程"
        ),
        Schedule(
            "软件研发部 后端组 Springboot入门",
            int(time.time() + 86400 * 2),
            int(time.time() + 86400 * 2 + 7200),
            "大学生活动中心-113",
            "学习Spring框架"
        ),
        Schedule(
            "软件研发部 Python组 第一次授课",
            int(time.time() + 86400),
            int(time.time() + 86400 + 7200),
            "大学生活动中心-101",
            "Python基础入门课程"
        ),
        Schedule(
            "软件研发部 后端组 Springboot入门",
            int(time.time() + 86400 * 2),
            int(time.time() + 86400 * 2 + 7200),
            "大学生活动中心-113",
            "学习Spring框架"
        ),
    ]
    creat_poster("软件研发部", schs)
