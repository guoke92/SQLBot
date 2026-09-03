---
type: enum
title: wf_status
page_key: wf_status
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# wf_status

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 tenant_project_approval.wf_status；db 实测分布，基线外 1 值。）

```ground:enum
enum: wf_status
fields: [tenant_project_approval.wf_status]
values:
  PENDING:
    label: 待发起
  RUNNING:
    label: 审批中
  FINISHED:
    label: 审批通过
  TERMINATED:
    label: 审批拒绝
  REVOKED:
    label: "REVOKED"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
