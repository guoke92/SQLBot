---
type: concept
title: 上下文 JSON
page_key: 上下文JSON
belong: concepts
domain: 异步任务与数据同步
status: published
aliases: ["ctxJson", "ctx_json"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
maps_to: "async_io_task.ctx_json"
field_targets: ["async_io_task.ctx_json"]
adjudication: "boundary"
also_confused_with: ["biz_args_json"]
scope:
  databases: [lowcode_pplatform]
---

上下文 JSON 存储执行上下文（userId/custId/companyType/dbTenantCode 等），不包含业务方法参数。相关表：[[async_io_task]]。

## 需求背景

需要区分执行上下文与方法实参。

## 版本演进

v0.1 建立术语边界。