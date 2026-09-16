---
type: rule
title: 立项统计不是上线审批
page_key: wechat_stats_not_online_approval
domain: 微企链立项与项目审批
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - wechat_project_approval_apply.sp_no
  - tenant_project_approval.wf_status
---

立项统计看 wechat_project_approval_apply；上线审批看 tenant_project_approval。用 wf_status 去滤立项行会空。

```ground:rule
name: 立项统计不是上线审批
content: 立项统计看 wechat_project_approval_apply；上线审批看 tenant_project_approval。用 wf_status 去滤立项行会空。
field_targets: [wechat_project_approval_apply.sp_no, tenant_project_approval.wf_status]
evidence: "code_path:ProjectStatisticsApplication.java:98"
```
