---
type: caliber
title: SaaS 立项统计范围
page_key: saas_initiation
domain: 微企链立项与项目审批
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - wechat_project_approval_apply.sp_type
  - wechat_project_approval_apply.act_procinst_status
---

立项统计页代码范围；system_delivery 还需 SaaS 或 Saas+本地化。

```ground:caliber
name: SaaS 立项统计范围
predicate: "wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.act_procinst_status IN ('1','2')"
scope: wechat_project_approval_apply
evidence: code
```
