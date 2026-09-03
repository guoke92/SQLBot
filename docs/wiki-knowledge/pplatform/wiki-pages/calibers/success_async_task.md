---
type: caliber
title: 成功异步任务
page_key: success_async_task
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [async_io_task.status]
scope:
  databases: [lowcode_pplatform]
---

成功异步任务口径定义：`async_io_task.status = 'SUCCESS'`，用于异步任务查询中过滤成功记录。

## 需求背景

异步任务查询常需统计或筛选成功任务，状态值由 [[async_io_task_status]] 定义。表 [[async_io_task]]。

## 版本演进

本页基于 db_dist:async_io_task.status 证据形成 v0.1 契约。

```ground:caliber
name: 成功异步任务
predicate: async_io_task.status = 'SUCCESS'
scope: 异步任务查询
evidence: db_dist:async_io_task.status
```