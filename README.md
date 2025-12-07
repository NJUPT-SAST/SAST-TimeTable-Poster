# SAST-TimeTable-Poster

## 简介

这是一个用来批量生成课程表的工具，用飞书API从日历中获取课程信息，并支持自定义修改课程信息后，用于生成课程表图片。

## 使用方法

安装python依赖

```bash
pip install -r requirements.txt
```

配置info.json文件，内容如下。联系软研获取详细info.json文件，并放入项目根目录下

```json
{
    "client_id": "你的Client ID",
    "client_secret": "你的Client Secret",
    "calendar_id": "课程表日历ID"
}
```

运行main.py

```bash
python main.py
```

生成的课程表图片会保存在output目录下
