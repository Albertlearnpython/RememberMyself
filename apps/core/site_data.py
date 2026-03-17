from django.urls import NoReverseMatch, reverse


SITE_TITLE = "RememberMyself"
SITE_TAGLINE = "安静的总索引"

SITE_MODULES = [
    {
        "key": "books",
        "title": "收藏书籍",
        "route_name": "books:index",
        "description": "阅读、笔记与归档放在同一处，像整理一间安静的阅览室。",
        "state": "首版开发",
        "available": True,
    },
    {
        "key": "food",
        "title": "喜欢的美食",
        "route_name": "core:food",
        "description": "收录喜欢的味道、照片和做法，把偏爱留下来。",
        "state": "设计中",
        "available": False,
    },
    {
        "key": "music",
        "title": "喜欢的音乐",
        "route_name": "music:index",
        "description": "收藏喜欢的音乐、封面与文件，把听过的东西安静归档下来。",
        "state": "首版开发",
        "available": True,
    },
    {
        "key": "scenery",
        "title": "喜欢的景色",
        "route_name": "scenery:index",
        "description": "手机上传照片，自动识别时间和地点，把风景和当时的心情一起保存下来。",
        "state": "首版开发",
        "available": True,
    },
    {
        "key": "fitness",
        "title": "健身养体",
        "route_name": "core:fitness",
        "description": "记录体重、饮食和趋势，让身体变化有连续性。",
        "state": "设计中",
        "available": False,
    },
    {
        "key": "finance",
        "title": "收支平衡",
        "route_name": "core:finance",
        "description": "让每日收入与花销留下轨迹，而不是散在聊天和记忆里。",
        "state": "设计中",
        "available": False,
    },
    {
        "key": "schedule",
        "title": "时间安排",
        "route_name": "core:schedule",
        "description": "以后会承接日程、提醒和时间块，把计划沉淀成秩序。",
        "state": "设计中",
        "available": False,
    },
    {
        "key": "methods",
        "title": "方法心得",
        "route_name": "core:methods",
        "description": "保存那些值得反复拿出来的方法、原则和心得。",
        "state": "设计中",
        "available": False,
    },
]


def get_site_modules():
    modules = []
    for module in SITE_MODULES:
        item = dict(module)
        try:
            item["path"] = reverse(item["route_name"])
        except NoReverseMatch:
            item["path"] = "#"
        modules.append(item)
    return modules
