---
type: concept
title: 异步批量处理
page_key: async_batch_term
belong: concepts
domain: remaining
status: draft
aliases: [文件管理, 异步导入导出]
maps_to: async_io_task.status
field_targets: [async_io_task.status, async_io_task.task_type, async_io_task.menu_code]
sources: ['code_path:AsyncIoTaskManager.java:84', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [async_io_task]
also_confused_with: [wechat_apply_term]
adjudication: boundary
---

# 异步批量处理

document_claim:异步批量处理.md#15：导入导出走 async_io_task，状态 PENDING/SUCCESS/FAILED（现网另有 RUNNING）。
企微立项导入只是其中一个 menu_code。不要把任务状态当成立项审批状态。

## 页面链接

- [[tables/async_io_task]]
- [[dicts/async_io_task__menu_code]]
- [[dicts/async_io_task__status]]
- [[dicts/async_io_task__task_type]]
- [[processes/async_io_task__status]]
- [[concepts/wechat_apply_term]]
