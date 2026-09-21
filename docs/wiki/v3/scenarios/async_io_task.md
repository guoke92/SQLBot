---
type: scenario
title: 异步导入导出任务
page_key: async_io_task
belong: scenarios
domain: remaining
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [async_io_task]
---

# 异步导入导出任务

异步导入导出任务

```ground:scenario
scenario: async_io_task
hubs:
- table: async_io_task
  role: master
lifecycle:
- dict: async_io_task__status
  process: async_io_task__status
```

## 页面链接

- [[tables/async_io_task]]
- [[dicts/async_io_task__status]]
- [[processes/async_io_task__status]]
