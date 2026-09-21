---
type: scenario
title: 企微立项审批单
page_key: wechat_project_approval
belong: scenarios
domain: remaining
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [wechat_project_approval_apply, wechat_project_approval_field_history]
---

# 企微立项审批单

企微立项审批单

```ground:scenario
scenario: wechat_project_approval
hubs:
- table: wechat_project_approval_apply
  role: master
shared:
- table: wechat_project_approval_field_history
  role: history
```

## 页面链接

- [[tables/wechat_project_approval_apply]]
- [[tables/wechat_project_approval_field_history]]
