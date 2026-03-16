# 收藏书籍字段设计

## 目标

这个文档把收藏书籍页从“概念设计”推进到“可实现的数据结构设计”。

原则：

- 字段不能只服务于管理
- 字段也要服务于阅读记忆
- 字段要兼顾公开展示与登录后的深层内容

## 数据对象划分

建议至少拆成三个核心对象：

1. `Book`
2. `BookTag`
3. `BookAsset`

如果以后需要扩展，还可以再加：

4. `BookReadingLog`

## 一、Book 字段

| 字段名 | 含义 | 类型 | 必填 | 前台展示 | 编辑角色 |
| --- | --- | --- | --- | --- | --- |
| `id` | 书籍唯一标识 | string/uuid | 是 | 否 | 系统 |
| `title` | 书名 | string | 是 | 是 | editor+ |
| `subtitle` | 副标题 | string | 否 | 可选 | editor+ |
| `author` | 作者 | string | 是 | 是 | editor+ |
| `translator` | 译者 | string | 否 | 可选 | editor+ |
| `publisher` | 出版社 | string | 否 | 可选 | editor+ |
| `publish_year` | 出版年份 | number | 否 | 可选 | editor+ |
| `isbn` | ISBN | string | 否 | 否 | editor+ |
| `language` | 语言 | enum | 否 | 可选 | editor+ |
| `cover_image_url` | 封面图 | string | 否 | 是 | editor+ |
| `cover_tone` | 封面主色调 | string | 否 | 否 | editor+ |
| `status` | 阅读状态 | enum | 是 | 是 | editor+ |
| `rating` | 主观评分（1-100） | number | 否 | 可选 | editor+ |
| `word_count` | 字数（单位：万，支持两位小数） | decimal | 否 | 可选 | editor+ |
| `tags` | 标签名数组（来自共享标签库） | string[] | 否 | 是 | editor+ |
| `short_review` | 一句短评 | string | 否 | 是 | editor+ |
| `long_note` | 长笔记 | markdown/text | 否 | 登录后/公开可配置 | editor+ |
| `why_it_matters` | 为什么重要 | text | 否 | 是 | editor+ |
| `reading_started_at` | 开始阅读时间 | date | 否 | 可选 | editor+ |
| `reading_finished_at` | 读完时间 | date | 否 | 可选 | editor+ |
| `revisit_count` | 重读次数 | number | 否 | 否 | editor+ |
| `visibility` | 展示可见性 | enum | 是 | 否 | owner/editor |
| `sort_order` | 排序权重 | number | 否 | 否 | editor+ |
| `created_at` | 创建时间 | datetime | 是 | 否 | 系统 |
| `updated_at` | 更新时间 | datetime | 是 | 否 | 系统 |

## 二、BookTag 字段

| 字段名 | 含义 | 类型 | 必填 | 前台展示 | 编辑角色 |
| --- | --- | --- | --- | --- | --- |
| `id` | 标签唯一标识 | string/uuid | 是 | 否 | 系统 |
| `name` | 标签名 | string | 是 | 是 | editor+ |
| `created_at` | 创建时间 | datetime | 是 | 否 | 系统 |

补充说明：

- 标签应当是全站书籍模块里的共享对象，不是每本书自己的私有字符串。
- 同一个标签可以被多本书复用，例如 `养生` 可以同时挂在多本书上。
- 如果编辑时输入了不存在的新标签，系统应自动创建并加入当前书籍。
- 标签颜色不单独存库，前端根据标签名做稳定映射，让同名标签在全站保持同一色调。

## 三、BookAsset 字段

| 字段名 | 含义 | 类型 | 必填 | 前台展示 | 编辑角色 |
| --- | --- | --- | --- | --- | --- |
| `id` | 资源唯一标识 | string/uuid | 是 | 否 | 系统 |
| `book_id` | 所属书籍 | string/uuid | 是 | 否 | 系统 |
| `asset_type` | 资源类型 | enum | 是 | 是 | editor+ |
| `file_name` | 文件名 | string | 是 | 是 | editor+ |
| `file_size` | 文件大小 | number | 否 | 是 | 系统 |
| `mime_type` | 文件格式 | string | 否 | 是 | 系统 |
| `storage_key` | 存储路径 | string | 是 | 否 | 系统 |
| `download_enabled` | 是否允许下载 | boolean | 是 | 否 | editor+ |
| `visibility` | 文件可见性 | enum | 是 | 否 | owner/editor |
| `created_at` | 上传时间 | datetime | 是 | 否 | 系统 |
| `updated_at` | 更新时间 | datetime | 是 | 否 | 系统 |

## 四、BookReadingLog 字段

这个对象不是当前第一优先级，但建议提前留概念。

| 字段名 | 含义 | 类型 |
| --- | --- | --- |
| `id` | 日志唯一标识 | string/uuid |
| `book_id` | 所属书籍 | string/uuid |
| `started_at` | 本轮开始时间 | date |
| `ended_at` | 本轮结束时间 | date |
| `phase_note` | 阶段备注 | text |

## 推荐枚举值

### `status`

- `planned`
- `reading`
- `finished`
- `revisiting`

### `visibility`

- `public`
- `login_required`
- `private`

### `asset_type`

- `pdf`
- `epub`
- `txt`
- `md`
- `other`

## 页面展示时最重要的字段

如果只是列表卡片，优先展示：

- `cover_image_url`
- `title`
- `author`
- `status`
- `word_count`
- `tags`
- `short_review`

如果是详情页，优先展示：

- `title`
- `author`
- `why_it_matters`
- `long_note`
- `reading_started_at`
- `reading_finished_at`
- `BookAsset`

## 字段设计的取舍

### 为什么保留 `why_it_matters`

因为这是这个页面和普通书单工具的核心差异。

普通书单管理的是“我有什么书”。

你这个页面更应该记录：

**这本书为什么进入了我的人生系统。**

### 为什么 `short_review` 和 `long_note` 都要有

因为它们服务的不是同一种展示层级。

- `short_review` 用于列表和摘要
- `long_note` 用于详情和深层阅读记录

### 为什么标签要改成共享标签库

因为标签不仅要“能显示”，还要“能复用和筛选”。

如果继续把标签存成逗号文本：

- 很难保证 `养生` 和 ` 养生 ` 被视为同一个标签
- 很难做多选
- 很难稳定地支持“新建一个标签并给多本书共用”

改成共享标签对象后：

- 同名标签天然复用
- 书籍可以稳定多选多个标签
- 新标签创建后可以立刻被后续书籍继续使用

### 为什么 `visibility` 要放在书和文件两个层面

因为以后可能会出现：

- 书籍信息公开
- 文件本身需登录

也可能出现：

- 某本书整体只对登录可见

所以要允许书与资源分层控制。

## 当前字段结论

这一版字段已经足够支撑：

- 公开书单展示
- 登录后下载受保护文件
- 抽屉式新增与编辑
- 封面展示与书籍归档

它适合作为第一版正式实现的数据字段基线。
