# 收藏书籍模块：信息补全接口与状态说明

## 已落地范围

当前版本已经实现以下能力：

- 入口位于“书籍编辑抽屉”顶部，仅编辑已有书籍时显示
- 补全来源支持 `微信读书 / 豆瓣 / Open Library`
- 点击“获取预览”后，先返回字段差异预览
- 你可以在弹窗里勾选要覆盖的字段
- 点击“确认填入”后，只会把字段填回当前编辑表单
- 最终仍需点击抽屉底部“保存”，才会真正写入数据库
- 搜不到、来源暂不可用、没有差异字段时，统一走轻提示 toast

## 接口

### `POST /books/:id/metadata-preview/`

用途：

- 根据当前书籍和指定来源拉取候选信息
- 生成字段级差异
- 返回短时有效的 `previewToken`

请求示例：

```json
{
  "provider": "weread",
  "query": "苏菲的世界"
}
```

返回示例：

```json
{
  "success": true,
  "status": "found",
  "previewToken": "eyJib29rX2lkIjoxLCJwcm92aWRlciI6IndlcmVhZCIsLi4u",
  "provider": {
    "id": "weread",
    "label": "微信读书"
  },
  "candidate": {
    "sourceId": "27172839",
    "title": "苏菲的世界",
    "subtitle": "",
    "author": "乔斯坦·贾德",
    "translator": "萧宝森",
    "publisher": "作家出版社",
    "coverImageUrl": "https://example.com/cover.jpg",
    "intro": "这是一本风靡世界的哲学启蒙书。",
    "shortReview": "这是一本风靡世界的哲学启蒙书"
  },
  "fields": [
    {
      "name": "cover_image_url",
      "label": "封面图链接",
      "current": "",
      "incoming": "https://example.com/cover.jpg",
      "changed": true,
      "defaultSelected": true
    },
    {
      "name": "translator",
      "label": "译者",
      "current": "",
      "incoming": "萧宝森",
      "changed": true,
      "defaultSelected": true
    },
    {
      "name": "publisher",
      "label": "出版社",
      "current": "旧出版社",
      "incoming": "作家出版社",
      "changed": true,
      "defaultSelected": false
    }
  ]
}
```

状态说明：

- `found`：找到候选结果，弹出预览弹窗
- `not_found`：没搜到，显示 3 秒 toast
- `unavailable`：来源请求失败或超时，显示 3 秒 toast
- `no_changes`：找到了书，但当前没有可补全的差异字段，显示 3 秒 toast

### `POST /books/:id/metadata-apply/`

用途：

- 校验 `previewToken`
- 只返回你选中的字段和值
- 前端把这些值写回当前编辑表单

请求示例：

```json
{
  "previewToken": "eyJib29rX2lkIjoxLCJwcm92aWRlciI6IndlcmVhZCIsLi4u",
  "fields": [
    "cover_image_url",
    "translator"
  ]
}
```

返回示例：

```json
{
  "success": true,
  "updatedFields": [
    "cover_image_url",
    "translator"
  ],
  "values": {
    "cover_image_url": "https://example.com/cover.jpg",
    "translator": "萧宝森"
  },
  "message": "已将 2 个字段填入当前表单，请继续点击保存。"
}
```

失败说明：

- `preview token expired`：预览已过期，需要重新获取预览
- `preview token invalid / mismatch`：预览校验失败
- `no fields selected`：没有选择任何字段

## 当前允许补全的字段

- `cover_image_url`
- `author`
- `translator`
- `publisher`
- `subtitle`
- `short_review`

默认勾选规则：

- 当前字段为空：默认勾选
- 当前字段已有内容：默认不勾选
- 当前字段和外部结果完全一致：不显示在差异列表里

## 页面状态

### 1. 待机状态

- 编辑抽屉顶部显示来源下拉框
- “获取预览”按钮可点击

### 2. 加载预览

- “获取预览”按钮进入禁用态
- 按钮文案切到“获取中…”

### 3. 预览成功

- 打开弹窗
- 上半区显示候选书籍卡片
- 下半区显示字段差异列表
- 右下角按钮为“确认填入”

### 4. 预览失败

- 不打断抽屉
- 右上角或底部显示轻提示 toast
- 3 秒后自动消失

### 5. 确认填入

- 只修改当前表单里的对应输入框
- 不直接保存数据库
- 弹窗关闭
- toast 提示“已将 X 个字段填入当前表单，请继续点击保存”

## 前端交互原则

- 书籍列表页不放补全入口，避免把维护动作混进浏览态
- 只在编辑抽屉里处理，保持“单本书、单次确认”的心智模型
- 用轻提示处理失败，避免大面积遮挡手机屏幕
- 预览弹窗保留字段级勾选，避免无意覆盖你已经写过的内容
