# 文档总索引

这个目录现在按“规划 / 设计 / 历史”三类整理。

优先阅读顺序建议如下：

1. 先看页面设计
2. 再看需求历史
3. 最后看整体规划与技术方案

## 目录结构

```text
docs/
├─ design/
│  ├─ home/
│  └─ books/
├─ history/
└─ planning/
```

## 1. 页面设计

### 首页

- [首页设计概览（中文）](./design/home/overview.zh-CN.md)
- [首页高保真说明（中文）](./design/home/visual-spec.zh-CN.md)
- [首页版式深化说明（中文）](./design/home/ui-composition.zh-CN.md)
- [首页最终视觉稿说明（中文）](./design/home/final-visual-spec.zh-CN.md)
- [Home Design Overview (English)](./design/home/overview.en.md)

### 收藏书籍

- [收藏书籍设计概览（中文）](./design/books/overview.zh-CN.md)
- [收藏书籍高保真说明（中文）](./design/books/visual-spec.zh-CN.md)
- [收藏书籍字段设计（中文）](./design/books/data-fields.zh-CN.md)
- [收藏书籍交互与手机端说明（中文）](./design/books/interaction-flow.zh-CN.md)
- [收藏书籍最终视觉稿说明（中文）](./design/books/final-visual-spec.zh-CN.md)
- [Books Design Overview (English)](./design/books/overview.en.md)

## 2. 需求历史

- [需求历史（中文）](./history/request-history.zh-CN.md)
- [Request History (English)](./history/request-history.en.md)

## 3. 整体规划

目前这部分仍以英文版为主，后续再逐步补中文。

- [Site Blueprint](./planning/site-blueprint.en.md)
- [Technical Plan](./planning/technical-plan.en.md)
- [Page Wireframes](./planning/page-wireframes.en.md)
- [Module Architecture](./planning/module-architecture.en.md)
- [Data Models](./planning/data-models.en.md)

## 当前已确认的设计决定

- 网站不是展示型官网，而是个人人生系统
- 首页是“安静的总索引”
- 视觉基调是“简约 + 工艺美感 + 冷静的诗意”
- 收藏书籍页采用抽屉式编辑
- 收藏书籍页当前字段结构先保持现有方案
- 首页继续深化到更接近正式 UI 的版式说明
- 收藏书籍页已经补充字段设计和手机端交互方案
- 首页已经补足正式跳转规则和最终视觉规格
- 收藏书籍页已经进入前端可直接照着实现的视觉规格层
- 文档以后统一按板块分类，不再平铺在根目录
