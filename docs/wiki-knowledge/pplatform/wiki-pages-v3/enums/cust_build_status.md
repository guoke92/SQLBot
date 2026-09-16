---
type: enum
title: cust_build_status
page_key: cust_build_status
domain: 企业建档与认证状态机
status: draft
aliases: [建档状态, 企业认证状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustBuildStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [cust_build_status_flow]
---

# cust_build_status

认证/建档过程。label 取客户模块 `CustBuildStatusEnum`（`CUST_BUILDING` 为「审核中」；common-api 同名枚举写作「审批中」）。企业主档流转见 [[cust_build_status_flow]]。

同一字典还出现在联系人 `cust_build_status`（常从企业拷贝）和邀请 `progress`。与账号激活 [[activate_status]]、企业 [[cust_status]] 不是同一列。

```ground:enum
enum: cust_build_status
fields:
  - cust_company_info.cust_build_status
  - cust_person_info.cust_build_status
  - cust_invite_info.progress
values:
  "INIT":
    label: "初始化"
  "TO_BE_BUILD":
    label: "未建档"
  "BUILDING":
    label: "建档中"
  "BUILD_SUCCESS":
    label: "认证成功"
  "BUILD_FAIL":
    label: "认证失败"
  "BUILD_BACK":
    label: "退回"
  "BUILD_ACTIVATE":
    label: "待激活"
  "CUST_CONFIRM_AWAIT":
    label: "待客户认证"
  "CUST_AUDIT_AWAIT":
    label: "待审核"
  "CUST_BUILDING":
    label: "审核中"
  "CUST_BUILD_SUCCESS":
    label: "审核通过"
  "CUST_BUILD_FAIL":
    label: "审核拒绝"
  "CUST_CHANGE":
    label: "变更"
  "AWAIT_CUST_CONFIRM":
    label: "待客户确认"
```
