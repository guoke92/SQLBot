---
type: concept
title: 参数 JSON
page_key: 参数JSON
domain: 异步任务与数据同步
status: published
aliases: ["bizArgsJson", "biz_args_json"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
maps_to: "async_io_task.biz_args_json"
field_targets: ["async_io_task.biz_args_json"]
adjudication: "boundary"
also_confused_with: ["ctx_json"]
scope:
  databases: [lowcode_pplatform]
---

参数 JSON 存储业务方法实参，与执行上下文 ctx_json 不同。相关表：[[async_io_task]]。

## 需求背景

需要区分方法参数与运行上下文。

## 版本演进

v0.1 建立术语边界。