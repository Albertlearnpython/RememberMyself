# 文档总索引

这个目录现在按：

- 设计
- 实现
- 历史
- 规划

四层来整理。

## 当前优先阅读顺序

1. 先看首页与书籍页的设计文档
2. 再看全站色彩系统
3. 再看实现层文档
4. 最后看需求历史

## 当前最重要的文档

### 首页（当前版本）

- [首页设计概览](./design/home/overview.zh-CN.md)
- [首页高保真说明](./design/home/visual-spec.zh-CN.md)
- [首页版式深化说明](./design/home/ui-composition.zh-CN.md)
- [首页最终视觉稿说明](./design/home/final-visual-spec.zh-CN.md)
- [首页五条流带设计稿](./design/home/memory-streams.zh-CN.md)

### 全站色彩系统（当前版本）

- [全站色彩系统方案](./design/system/color-system.zh-CN.md)

### 首页实现层

- [首页模块实现说明](./implementation/modules/home-module-spec.zh-CN.md)

## 目录结构

```text
docs/
├─ design/
│  ├─ system/
│  ├─ home/
│  ├─ books/
│  ├─ articles/
│  ├─ music/
│  ├─ food/
│  ├─ scenery/
│  ├─ fitness/
│  ├─ finance/
│  ├─ schedule/
│  ├─ methods/
│  └─ all-modules/
├─ implementation/
│  ├─ system/
│  └─ modules/
├─ history/
└─ planning/
```

## 设计文档

### 首页

- [首页设计概览（中文）](./design/home/overview.zh-CN.md)
- [首页高保真说明（中文）](./design/home/visual-spec.zh-CN.md)
- [首页版式深化说明（中文）](./design/home/ui-composition.zh-CN.md)
- [首页最终视觉稿说明（中文）](./design/home/final-visual-spec.zh-CN.md)
- [首页五条流带设计稿（中文）](./design/home/memory-streams.zh-CN.md)

### 收藏书籍

- [收藏书籍设计概览（中文）](./design/books/overview.zh-CN.md)
- [收藏书籍高保真说明（中文）](./design/books/visual-spec.zh-CN.md)
- [收藏书籍字段设计（中文）](./design/books/data-fields.zh-CN.md)
- [收藏书籍交互与手机端说明（中文）](./design/books/interaction-flow.zh-CN.md)
- [收藏书籍最终视觉稿说明（中文）](./design/books/final-visual-spec.zh-CN.md)
- [收藏书籍外部信息补全设计（中文）](./design/books/metadata-enrichment.zh-CN.md)

### 文章

- [文章最终视觉稿说明（中文）](./design/articles/final-visual-spec.zh-CN.md)

### 喜欢的音乐 / 美食 / 其他板块

- [喜欢的音乐最终视觉稿说明（中文）](./design/music/final-visual-spec.zh-CN.md)
- [喜欢的美食最终视觉稿说明（中文）](./design/food/final-visual-spec.zh-CN.md)
- [喜欢的景色最终视觉稿说明（中文）](./design/scenery/final-visual-spec.zh-CN.md)
- [健身养体最终视觉稿说明（中文）](./design/fitness/final-visual-spec.zh-CN.md)
- [收支平衡最终视觉稿说明（中文）](./design/finance/final-visual-spec.zh-CN.md)
- [时间安排最终视觉稿说明（中文）](./design/schedule/final-visual-spec.zh-CN.md)
- [方法心得最终视觉稿说明（中文）](./design/methods/final-visual-spec.zh-CN.md)

## 实现文档

- [实现层文档总索引](./implementation/README.zh-CN.md)
- [前端组件规范](./implementation/system/frontend-component-spec.zh-CN.md)
- [接口草案总规范](./implementation/system/api-draft.zh-CN.md)
- [状态机总规范](./implementation/system/state-machine-conventions.zh-CN.md)
- [首页模块实现说明](./implementation/modules/home-module-spec.zh-CN.md)
- [收藏书籍模块实现说明](./implementation/modules/books-module-spec.zh-CN.md)
- [文章模块实现说明](./implementation/modules/articles-module-spec.zh-CN.md)
- [喜欢的音乐模块实现说明](./implementation/modules/music-module-spec.zh-CN.md)

## 需求历史

- [需求历史（中文）](./history/request-history.zh-CN.md)

## 当前确认过的关键设计决定

- 首页是“安静的总索引”，不是展示型官网
- 首页主结构已经固定为：个人档案卡 + 介绍主卡 + 模块索引 + 五条流带
- 首页色调已经从偏黄路线切换为冷白底上的高级多彩路线
- 五条流带已经是首页固定结构，不再是临时想法
- 收藏书籍模块定位已经收敛为：封面展示 + 附件归档 + 下载
- 文章模块当前定位已经收敛为：Markdown 上传 + 下载 + 覆盖 + 渲染展示
- 音乐模块当前只做上传、下载、展示，不做在线播放
- 文档以后优先维护中文版本，过时口径直接更新，不继续挂旧方案
