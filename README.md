# RememberMyself

`RememberMyself` 是一个“人生系统网站”项目。

当前阶段已经进入正式开发。

目前已经落地：

- 首页“五条记忆溪流”
- 收藏书籍第一版
- 文章第一版（Markdown 上传 / 下载 / 覆盖 / 展示）
- 喜欢的音乐第一版（上传 / 下载 / 展示）

## 项目方向

这个网站不是普通博客，也不是展示型主页。

它更像一个长期运作的个人系统，用来：

- 记住我是谁
- 保存我真正喜欢的东西
- 记录身体、时间、收支和方法
- 把数据、习惯、记忆和反思整理成可持续沉淀的个人档案

## 当前设计基调

- 简约
- 工艺美感
- 冷静的诗意
- 克制、精确、留白
- 心灵的极简主义

当前色彩系统已开始切换到：

> 静雾档案

首页的核心口吻已经确定为：

> 首页不是“展示型官网”，而是“安静的总索引”。

## 核心原则

- 模块独立：每个页面以后都应该可以独立扩展、改版、重构。
- 公开阅读：网站内容可以公开浏览。
- 登录编辑：编辑行为必须登录后才可见。
- 资源保护：书籍和音乐等文件资源需要登录后访问。
- 数据与叙事并存：页面既要能记录数据，也要能保存记忆与意义。
- 敏感信息隔离：账号、密码、密钥等内容不进入网站和仓库。
- 手机优先考虑：后续正式实现时要考虑手机使用体验。

## 页面规划

1. 首页
2. 收藏书籍
3. 文章
4. 喜欢的美食
5. 喜欢的音乐
6. 喜欢的景色
7. 健身养体
8. 收支平衡
9. 时间安排
10. 方法心得

## 文档导航

中文优先入口：

- [文档总索引（中文）](./docs/README.zh-CN.md)
- [首页设计概览（中文）](./docs/design/home/overview.zh-CN.md)
- [全站色彩系统方案（中文）](./docs/design/system/color-system.zh-CN.md)
- [首页高保真说明（中文）](./docs/design/home/visual-spec.zh-CN.md)
- [首页版式深化说明（中文）](./docs/design/home/ui-composition.zh-CN.md)
- [首页最终视觉稿说明（中文）](./docs/design/home/final-visual-spec.zh-CN.md)
- [收藏书籍设计概览（中文）](./docs/design/books/overview.zh-CN.md)
- [收藏书籍高保真说明（中文）](./docs/design/books/visual-spec.zh-CN.md)
- [收藏书籍字段设计（中文）](./docs/design/books/data-fields.zh-CN.md)
- [收藏书籍交互与手机端说明（中文）](./docs/design/books/interaction-flow.zh-CN.md)
- [收藏书籍最终视觉稿说明（中文）](./docs/design/books/final-visual-spec.zh-CN.md)
- [文章最终视觉稿说明（中文）](./docs/design/articles/final-visual-spec.zh-CN.md)
- [喜欢的美食最终视觉稿说明（中文）](./docs/design/food/final-visual-spec.zh-CN.md)
- [喜欢的音乐最终视觉稿说明（中文）](./docs/design/music/final-visual-spec.zh-CN.md)
- [全站板块成熟度总览（中文）](./docs/design/all-modules/initial-overview.zh-CN.md)
- [健身养体最终视觉稿说明（中文）](./docs/design/fitness/final-visual-spec.zh-CN.md)
- [收支平衡最终视觉稿说明（中文）](./docs/design/finance/final-visual-spec.zh-CN.md)
- [喜欢的景色最终视觉稿说明（中文）](./docs/design/scenery/final-visual-spec.zh-CN.md)
- [时间安排最终视觉稿说明（中文）](./docs/design/schedule/final-visual-spec.zh-CN.md)
- [方法心得最终视觉稿说明（中文）](./docs/design/methods/final-visual-spec.zh-CN.md)
- [实现层文档总索引（中文）](./docs/implementation/README.zh-CN.md)
- [前端组件规范（中文）](./docs/implementation/system/frontend-component-spec.zh-CN.md)
- [接口草案总规范（中文）](./docs/implementation/system/api-draft.zh-CN.md)
- [状态机总规范（中文）](./docs/implementation/system/state-machine-conventions.zh-CN.md)
- [首页模块实现说明（中文）](./docs/implementation/modules/home-module-spec.zh-CN.md)
- [收藏书籍模块实现说明（中文）](./docs/implementation/modules/books-module-spec.zh-CN.md)
- [文章模块实现说明（中文）](./docs/implementation/modules/articles-module-spec.zh-CN.md)
- [喜欢的美食模块实现说明（中文）](./docs/implementation/modules/food-module-spec.zh-CN.md)
- [喜欢的音乐模块实现说明（中文）](./docs/implementation/modules/music-module-spec.zh-CN.md)
- [喜欢的景色模块实现说明（中文）](./docs/implementation/modules/scenery-module-spec.zh-CN.md)
- [健身养体模块实现说明（中文）](./docs/implementation/modules/fitness-module-spec.zh-CN.md)
- [收支平衡模块实现说明（中文）](./docs/implementation/modules/finance-module-spec.zh-CN.md)
- [时间安排模块实现说明（中文）](./docs/implementation/modules/schedule-module-spec.zh-CN.md)
- [方法心得模块实现说明（中文）](./docs/implementation/modules/methods-module-spec.zh-CN.md)
- [喜欢的景色初步设计说明（中文）](./docs/design/scenery/initial-spec.zh-CN.md)
- [健身养体初步设计说明（中文）](./docs/design/fitness/initial-spec.zh-CN.md)
- [收支平衡初步设计说明（中文）](./docs/design/finance/initial-spec.zh-CN.md)
- [时间安排初步设计说明（中文）](./docs/design/schedule/initial-spec.zh-CN.md)
- [方法心得初步设计说明（中文）](./docs/design/methods/initial-spec.zh-CN.md)
- [需求历史（中文）](./docs/history/request-history.zh-CN.md)

英文/原始规划文档：

- [Site Blueprint](./docs/planning/site-blueprint.en.md)
- [Technical Plan](./docs/planning/technical-plan.en.md)
- [Page Wireframes](./docs/planning/page-wireframes.en.md)
- [Module Architecture](./docs/planning/module-architecture.en.md)
- [Data Models](./docs/planning/data-models.en.md)
- [Home Design Overview](./docs/design/home/overview.en.md)
- [Books Design Overview](./docs/design/books/overview.en.md)
- [Request History](./docs/history/request-history.en.md)

## 当前状态

- 已完成：总体架构规划与中文优先文档整理
- 已完成：首页“五条记忆溪流”第一版
- 已完成：收藏书籍第一版
- 已完成：文章第一版数据模型、Markdown 上传下载、覆盖与详情渲染
- 已完成：喜欢的音乐第一版数据模型、上传下载和详情页
- 已完成：首页 `声纹流` 接入真实音乐数据
- 已完成：全站色彩系统切换的第一轮施工
- 下一步：继续收口首页、书籍页、音乐页视觉细节，并推进美食 / 景色等模块
