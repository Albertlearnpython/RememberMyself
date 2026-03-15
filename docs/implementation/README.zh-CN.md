# 实现层文档总索引

这一层文档的目标，不是继续讨论页面长什么样，而是回答：

- 前端应该拆成哪些组件
- 每个页面需要哪些接口
- 页面状态如何流转
- 后续正式开发时，应该先搭哪一层

## 目录结构

```text
docs/implementation/
├─ system/
└─ modules/
```

## 阅读顺序

1. 先看系统级规范
2. 再看每个页面的模块实现说明
3. 开发时按页面逐个落地

## 系统级规范

- [前端组件规范（中文）](./system/frontend-component-spec.zh-CN.md)
- [接口草案总规范（中文）](./system/api-draft.zh-CN.md)
- [状态机总规范（中文）](./system/state-machine-conventions.zh-CN.md)

## 页面模块实现说明

- [首页模块实现说明（中文）](./modules/home-module-spec.zh-CN.md)
- [收藏书籍模块实现说明（中文）](./modules/books-module-spec.zh-CN.md)
- [喜欢的美食模块实现说明（中文）](./modules/food-module-spec.zh-CN.md)
- [喜欢的音乐模块实现说明（中文）](./modules/music-module-spec.zh-CN.md)
- [喜欢的景色模块实现说明（中文）](./modules/scenery-module-spec.zh-CN.md)
- [健身养体模块实现说明（中文）](./modules/fitness-module-spec.zh-CN.md)
- [收支平衡模块实现说明（中文）](./modules/finance-module-spec.zh-CN.md)
- [时间安排模块实现说明（中文）](./modules/schedule-module-spec.zh-CN.md)
- [方法心得模块实现说明（中文）](./modules/methods-module-spec.zh-CN.md)

## 当前结论

现在文档已经分成四层：

1. `planning`：总方向和架构原则
2. `design`：页面视觉与交互终稿
3. `implementation`：前端组件、接口、状态机实现说明
4. `history`：需求演进记录

这意味着后续真正开始开发时，不需要再从空白页起草方案。
