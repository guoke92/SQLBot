---
type: process
title: 联系人账号状态机
page_key: person_account_status
domain: 客户中心
status: draft
aliases:
  - 联系人状态流转
  - 管理员状态流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:ifNessaryFrzAdm
contract_version: "0.1"
belong: processes
---

联系人账号状态机描述 [[cust_person_info]].status 在管理员生效/冻结等动作下的流转，与 [[admin]]、[[available_admin]] 口径配合使用。状态来源为 CustPersonStatusConstant（code_const）。

```ground:process
name: 联系人账号状态机
field: cust_person_info.status
states:
  - value: ADD
    label: 新增/待生效
    source: code_const
  - value: EFFECT
    label: 生效
    source: code_const
  - value: FREEZE
    label: 冻结
    source: code_const
transitions:
  - from: ADD
    event: 保存法人作为管理员
    to: EFFECT
    evidence: code_path:CustPersonApplication.java:ifNessaryFrzAdm
  - from: EFFECT
    event: 管理员变更/手机号变更冻结旧管理员
    to: FREEZE
    evidence: code_path:CustPersonApplication.java:ifNessaryFrzAdm
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。