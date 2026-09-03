---
type: caliber
title: 未软删除异步任务
page_key: not_deleted_async_task
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [async_io_task.is_deleted]
scope:
  databases: [lowcode_pplatform]
---

未软删除异步任务口径定义：`async_io_task.is_deleted = '0'`，用于异步任务查询中排除已软删除记录。

## 需求背景

异步任务采用软删除标识 `is_deleted`，查询时需过滤已删除任务。表 [[async_io_task]]。

## 版本演进

本页基于 db_dist:async_io_task.is_deleted 证据形成 v0.1 契约。

```ground:caliber
name: 未软删除异步任务
predicate: async_io_task.is_deleted = '0'
scope: 异步任务查询
evidence: db_dist:async_io_task.is_deleted
```