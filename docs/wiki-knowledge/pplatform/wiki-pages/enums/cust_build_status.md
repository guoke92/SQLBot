---
type: enum
title: cust_build_status
page_key: cust_build_status
domain: 基线
status: draft
aliases: [审核中, 待客户认证]
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# cust_build_status

（权威枚举页：14 值，绑定方式 setter-evidence，主承载 cust_company_info.cust_build_status；db 实测分布。）

```ground:enum
enum: cust_build_status
fields: [cust_company_info.cust_build_status, cust_invite_info.progress, cust_person_info.cust_build_status]
values:
  INIT:
    label: 初始化
  CUST_CONFIRM_AWAIT:
    label: 待客户确认
  CUST_BUILDING:
    label: 审批中
  BUILD_BACK:
    label: 退回
  BUILD_FAIL:
    label: 认证失败
  BUILD_SUCCESS:
    label: 认证成功
  BUILD_ACTIVATE:
    label: 待激活
  TO_BE_BUILD:
    label: 未建档
  BUILDING:
    label: 建档中
  CUST_AUDIT_AWAIT:
    label: 待审核
  CUST_BUILD_SUCCESS:
    label: 审核通过
  CUST_BUILD_FAIL:
    label: 审核拒绝
  CUST_CHANGE:
    label: 变更
  AWAIT_CUST_CONFIRM:
    label: 待客户确认
```

## 表述差异

- CUST_BUILDING: 权威「审批中」；另有表述 ['审核中']
- CUST_CONFIRM_AWAIT: 权威「待客户确认」；另有表述 ['待客户认证']
