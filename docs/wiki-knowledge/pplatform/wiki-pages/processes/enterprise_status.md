---
type: process
title: 企业状态机
page_key: processes/enterprise-status
domain: AMS联系人第三方对接
status: published
aliases: [企业状态, 企业生命周期]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

企业状态机描述企业在 ADD/EFFECT/FREEZE/WRITEOFF/CHANGE 之间的迁移，支撑企业生命周期管理。

## 需求背景
企业管理中冻结、注销、变更均依赖该状态机，相关操作代码集中在 CustCompanyInfoApplication.custStatusOperator 和 submitForSimpleAuth。

## 版本演进
初始版本基于代码枚举和迁移逻辑提取。

```ground:process
name: 企业状态机
field: CustCompanyInfoDO.custStatus
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: code_enum
transitions:
  - from: EFFECT
    event: freeze
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.custStatusOperator"
  - from: FREEZE
    event: unfreeze
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.custStatusOperator"
  - from: EFFECT
    event: disable
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.custStatusOperator"
  - from: WRITEOFF
    event: enable
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.custStatusOperator"
  - from: ADD
    event: submit/approve
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.submitForSimpleAuth"
```

[[cust_company_info_do]] [[企业建档状态机]]