---
type: caliber
title: 未删除异步任务口径（is_deleted='0'）
page_key: async_io_task_not_deleted
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [未删除异步任务, is_deleted='0', NOT_DELETED]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.pageByUser / getByTaskNo / softDelete 中 NOT_DELETED='0'"
contract_version: "0.1"
belong: calibers
---

「未删除异步任务」是所有任务查询与软删操作的可见性口径：文件管理分页、按任务号查询都以 `is_deleted='0'` 过滤，软删时置为 '1'。注意该列是字符串 0/1，不是 Y/N。

表结构见 [[async_io_task]]，状态口径见 [[async_io_task_status]]。

## 需求背景
任务记录需要保留可追溯，删除只做逻辑删除，不物理清理。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 未删除异步任务
predicate: "async_io_task.is_deleted = '0'"
scope: "文件管理分页、按任务号查询、任务号软删"
evidence: "code:AsyncIoTaskManager.pageByUser / getByTaskNo / softDelete 中 NOT_DELETED='0'"
```