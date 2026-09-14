---
type: caliber
title: 同步失败记录存量口径
page_key: sync_error_retained_scope
domain: 平台事件监听与同步
status: draft
aliases:
  - enable=N 口径
  - 失败记录保留口径
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
contract_version: "0.1"
belong: calibers
---

查询 [[client_api_sync_error]] 时，`enable='N'` 是存量记录的默认观测值，应被理解为「已登记失败/已终止重试」的记录集合，而不是停用配置。

## 需求背景

同步失败需要留痕以便排查与人工重放，因此失败登记后即置 N；表结构默认 Y 只是新增记录的初始值，不代表现存数据分布。统计失败量时若按 `enable='Y'` 过滤会得到空集。

## 版本演进

- 存量 2227 行全部为 N，且 `retry_num` 常驻 3，说明这批记录已不再被重试消费。
- 与 [[cust_build_record]] 的补偿集合不同：后者以状态列（PENDING/RETRYING）而非 `enable` 表达可重试性，见 [[compensation_retry_task_filter]]。

```ground:caliber
name: 同步失败记录存量口径
predicate: "client_api_sync_error.enable = 'N'"
scope: 存量 2227 行全部为 N，作为“已登记失败/已终止重试”记录保留
evidence: db
```