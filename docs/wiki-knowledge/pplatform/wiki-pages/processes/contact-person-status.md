---
type: process
title: 联系人状态机
page_key: contact-person-status
belong: processes
domain: AMS联系人第三方对接
status: published
aliases: [人员状态, 联系人状态]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

联系人状态机描述企业联系人在 ADD/EFFECT/FREEZE 之间的迁移，支撑联系人生命周期管理。

## 需求背景
新增联系人保存后进入 EFFECT；通过 simpleChangePerson 冻结人员；通过 ifNessaryFrzAdm 解冻或必要的冻结操作。

## 版本演进
初始版本基于代码枚举和迁移逻辑提取。

```ground:process
name: 联系人状态机
field: CustPersonInfoDO.status
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
transitions:
  - from: ADD
    event: saveOrUpdate
    to: EFFECT
    evidence: "code_path:CustPersonInfoDO保存逻辑"
  - from: EFFECT
    event: freezePerson
    to: FREEZE
    evidence: "code_path:CustPersonApplication.simpleChangePerson"
  - from: FREEZE
    event: unfreeze
    to: EFFECT
    evidence: "code_path:CustPersonApplication.ifNessaryFrzAdm"
```

[[cust_person_info_do]] [[enterprise_contact]] [[admin]]