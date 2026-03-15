# 前端组件规范

## 目标

这份文档定义全站前端组件拆分的共同规则。

它解决的是：

- 组件怎么分层
- 命名怎么统一
- 哪类逻辑应该放在页面层，哪类应该放到功能组件层

## 组件分层

建议统一拆成 5 层：

1. `app shell`
2. `page`
3. `section`
4. `entity`
5. `overlay / form`

### 1. app shell

负责：

- 顶层布局
- 路由切换
- 登录态注入
- 全局主题变量

示例：

- `AppShell`
- `TopNav`
- `ModulePanel`

### 2. page

负责：

- 当前页面的数据编排
- 页面级 loading / error / empty
- 页面 section 排布

示例：

- `HomePage`
- `BooksPage`
- `FitnessPage`

### 3. section

负责：

- 页面内的大区块
- 一个区块内的展示和交互逻辑

示例：

- `HomeHeroSection`
- `BookListSection`
- `FinanceTrendSection`

### 4. entity

负责：

- 单个实体卡片、列表项、详情块

示例：

- `BookCard`
- `FoodCard`
- `MusicListItem`
- `MethodArticleCard`

### 5. overlay / form

负责：

- 抽屉
- 弹层
- 编辑表单
- 上传流程

示例：

- `BookEditorDrawer`
- `FoodEditorDrawer`
- `MusicPlayerPanel`

## 命名规则

统一推荐：

- 页面：`<Module>Page`
- 区块：`<Module><Section>NameSection`
- 列表：`<Module>List`
- 卡片：`<Module>Card`
- 详情：`<Module>DetailPanel`
- 抽屉：`<Module>EditorDrawer`

不要混用：

- `Modal` / `Drawer` 命名不一致
- `CardItem` / `ListCard` / `Block` 随意切换

## 文件组织建议

```text
src/
├─ app/
├─ shared/
│  ├─ ui/
│  ├─ hooks/
│  ├─ api/
│  └─ auth/
└─ features/
   ├─ home/
   ├─ books/
   ├─ food/
   ├─ music/
   ├─ scenery/
   ├─ fitness/
   ├─ finance/
   ├─ schedule/
   └─ methods/
```

每个 `feature` 下建议有：

- `components/`
- `api/`
- `state/`
- `types/`
- `utils/`

## 页面层职责边界

页面组件应该负责：

- 读取路由参数
- 请求页面主数据
- 组织 section
- 处理页面级错误和空态

页面组件不应该负责：

- 写复杂卡片 UI 细节
- 直接堆所有表单字段
- 混杂多个 overlay 的内部状态

## section 层职责边界

section 组件负责：

- 一个区块内的子组件组合
- 同区块的小状态
- 对单个数据片段做呈现

例如：

- `BooksListSection` 负责筛选、列表和空态
- `FinanceTrendSection` 负责范围切换和图表展示

## shared 组件建议

优先抽出复用价值高的组件：

- `PageHeader`
- `SearchInput`
- `FilterChipGroup`
- `EmptyState`
- `ErrorState`
- `MetricCard`
- `DetailPanel`
- `EditorDrawerShell`
- `AuthGatePanel`

## 受保护资源统一规则

书籍和音乐这类资源的访问区，统一建议封装成：

- `ProtectedAssetPanel`

它至少支持 4 个状态：

- `hidden`
- `locked`
- `ready`
- `error`

## 响应式规则

- 桌面端页面布局可以多栏
- 手机端必须主动重排，不允许机械压缩
- 多栏页面在手机端统一改为单列主流程

## 表单规则

- 所有抽屉表单统一使用分区标题
- 保存区固定在底部
- 支持脏状态提示
- 上传字段统一独立成一组

## 实现建议

第一版开发时，优先保证：

1. 组件边界清楚
2. 状态机简单可靠
3. 列表、详情、编辑三层关系清楚

不要一开始就追求过度抽象。
