import time
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, yes_no_dialog, message_dialog
from prompt_toolkit.styles import Style

from prompt_toolkit.key_binding import KeyBindings

from utils import Schedule

key_bindings = KeyBindings()


@key_bindings.add("escape")
def _(event):
    event.app.exit(None)


def info_text(sch):
    return f"""
课程信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
标题: {sch.title}
时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime(sch.start_time))} - {time.strftime('%H:%M', time.localtime(sch.end_time))}
地点: {sch.location}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

↑↓          选择操作
Enter/Space 确认操作
Tab         切换按钮
"""


def review_schedules(schedules):
    total = sum(len(schs) for schs in schedules.values())
    confirmed_schedules = {
        "软件研发部": [],
        "多媒体部": [],
        "电子部": [],
    }

    custom_style = Style.from_dict({
        'dialog': 'bg: #000000',
        'dialog frame.label': 'bg:#000000 #ffffff bold',
        'dialog.body': 'bg:#000000 #ffffff',
        'button': 'bg:#000000 #ffffff',
        'button.focused': 'reverse bold',
        'radio': '',
        'radio-checked': '',
        'radio-selected': 'reverse bold',
    })

    count = 0
    for dept, schs in schedules.items():
        if not schs:
            continue

        for idx, sch in enumerate(schs, 1):
            count += 1
            while True:
                # 显示选项对话框
                app = radiolist_dialog(
                    title=f"审查课程 - {dept} ({idx}/{len(schs)}) - 合计 ({count}/{total})",
                    text=info_text(sch),
                    values=[
                        ("confirm", "✓ 确定 - 添加到发布列表"),
                        ("skip", "✗ 忽略 - 跳过这个课程"),
                        ("edit_title", "✎ 修改标题"),
                        ("edit_location", "✎ 修改地点"),
                        # ("edit_description", "✎ 修改描述"),
                        # ("edit_start_time", "✎ 修改开始时间"),
                        # ("edit_end_time", "✎ 修改结束时间"),
                    ],
                    style=custom_style,
                    default="confirm"
                )
                app.key_bindings = key_bindings

                result = app.run()

                if result == "confirm":
                    confirmed_schedules[dept].append(sch)
                    break

                elif result == "skip":
                    skip_confirm = yes_no_dialog(
                        title="确认忽略",
                        text=f"确定要跳过「{sch.title}」吗？",
                        style=custom_style
                    ).run()
                    if skip_confirm:
                        break

                elif result == "edit_title":
                    new_title = input_dialog(
                        title="修改标题",
                        text="请输入新标题 (Esc 取消):",
                        default=sch.title,
                        style=custom_style
                    ).run()
                    if new_title:
                        sch.title = new_title
                        confirmed_schedules[dept].append(sch)
                        break

                elif result == "edit_location":
                    new_location = input_dialog(
                        title="修改地点",
                        text="请输入新地点 (Esc 取消):",
                        default=sch.location,
                        style=custom_style
                    ).run()
                    if new_location:
                        sch.location = new_location
                        confirmed_schedules[dept].append(sch)
                        break

                elif result is None:
                    # 用户按 Esc 取消
                    cancel_confirm = yes_no_dialog(
                        title="退出审查",
                        text="确定要退出审查吗？仅保存到当前结果",
                        style=custom_style
                    ).run()
                    if cancel_confirm:
                        return confirmed_schedules

    # 显示完成摘要
    summary_text = f"共确认 {sum(len(schs) for schs in confirmed_schedules.values())} 个课程将发布\n\n"
    for dept, schs in confirmed_schedules.items():
        summary_text += f"{dept+(1+(5-len(dept))*2)*' '}：{len(schs)} 个课程\n"
        # for sch in schs:
        #     summary_text += (f"{sch.title}\n")
        #     summary_text += (f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(sch.start_time))} - {time.strftime('%H:%M', time.localtime(sch.end_time))} | {sch.location}\n")
        #     summary_text += ("\n")

    message_dialog(
        title="✓ 审查完成",
        text=summary_text,
        style=custom_style
    ).run()

    return confirmed_schedules


if __name__ == "__main__":
    demo_schedules = {
        "软件研发部": [
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
        ],
        "多媒体部": [
            Schedule(
                "多媒体部 剪辑组授课",
                int(time.time() + 86400 * 3),
                int(time.time() + 86400 * 3 + 5400),
                "教三-101",
                "认识剪辑"
            ),
        ]
    }

    confirmed_schedules = review_schedules(demo_schedules)

