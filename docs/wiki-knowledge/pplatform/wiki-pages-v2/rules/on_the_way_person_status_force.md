---
type: rule
title: 在途企业人员状态强制初始化
page_key: on_the_way_person_status_force
domain: 租户迁移
status: draft
aliases: [在途人员状态强制 ADD]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
belong: rules
---

在途企业（`cust_status=ADD`）的管理员与经办人，状态一律覆写为 `CustPersonStatusConstant.ADD`，不采用上游报文里的状态值。这是 [[on_the_way_company]] 口径在人员链路的落地。

```ground:rule
name: 在途企业人员状态强制初始化
content: "company.cust_status=ADD 时，管理员/经办人 status 一律置 CustPersonStatusConstant.ADD，不采用上游推送状态"
impact: "防止在途数据把人员置为已生效"
field_targets:
  - cust_person_info.status
  - cust_company_info.cust_status
evidence: "code:PlatFormMigratoryApplication.java#setPersonAdm,#setPersonOper"
```

## 需求背景

人员生效状态直接关系到能否办理业务，迁移不能在在途企业下产出"已生效人员"。

## 版本演进

由采信上游人员状态改为按企业状态强制覆写，消除了上下游状态不一致导致的越权风险。

相关：[[cust_person_info]]、[[在途]]。