# 接口草案总规范

## 目标

这份文档定义全站接口草案的共同规则。

它不是后端最终协议，但足够支撑前端先行开发和 mock。

## 基础约定

### Base URL

- `/api`

### 响应格式

成功响应：

```json
{
  "success": true,
  "data": {},
  "meta": {}
}
```

失败响应：

```json
{
  "success": false,
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "Book not found"
  }
}
```

## 鉴权约定

- 公开读取接口无需登录
- 编辑接口必须登录
- 受保护资源读取接口必须登录

前端层面先按以下能力抽象：

- `session.user`
- `session.role`
- `session.isAuthenticated`

## 通用查询参数

列表接口统一优先支持：

- `q`
- `page`
- `page_size`
- `sort`
- `tag`
- `status`
- `date_from`
- `date_to`

## 通用分页格式

```json
{
  "success": true,
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 120
  }
}
```

## 上传约定

第一版可简化为普通 multipart 上传。

后续如果资源文件较大，再升级为：

1. 获取上传签名
2. 直传对象存储
3. 提交资源元数据

## 通用接口分层

建议至少分成：

- 页面摘要接口
- 列表接口
- 详情接口
- 新增接口
- 编辑接口
- 删除接口
- 资源接口

## 建议的会话接口

### `GET /api/session`

返回当前登录状态：

```json
{
  "success": true,
  "data": {
    "isAuthenticated": true,
    "role": "owner",
    "user": {
      "id": "u_1",
      "name": "owner"
    }
  }
}
```

## 错误码建议

- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `VALIDATION_ERROR`
- `UPLOAD_FAILED`
- `ASSET_LOCKED`

## 前端对接建议

- 每个 feature 自己维护 `api.ts`
- shared 层只维护 request client 和基础 error parser
- 前端先围绕文档 mock，不等后端最终实现
