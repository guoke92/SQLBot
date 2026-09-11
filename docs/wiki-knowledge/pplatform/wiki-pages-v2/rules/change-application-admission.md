---
type: rule
title: 变更申请准入校验
page_key: rule.change-application-admission
domain: 企业变更与运营变更
status: draft
aliases: [changeEnable, 变更准入]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeEnable
contract_version: "0.1"
---

企业 [[tables.cust_company_info]] 的 `check_status='CUST_CHECK_CHECKING'` 时 `changeEnable` 返回 false，不允许发起变更；企业不存在时同样返回 false。口径见 [[calibers.company-change-enable]]，与在途判定 [[rules.change-on-way-company]] 共同构成变更入口的两道闸门。

## 需求背景

企业准入审核在途期间，企业主体信息仍可能被审核结果改写，此时开放变更会产生两条互相冲突的审批链路；因此变更发起前必须做准入前置校验。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeEnable`。

```ground:rule
name: 变更申请准入校验
content: 企业 check_status='CUST_CHECK_CHECKING' 时 changeEnable 返回 false，不允许发起变更
impact: 变更提交前置校验；企业不存在时同样返回 false
field_targets:
  - cust_company_info.check_status
evidence: code_path:CustChangeApplication.java:changeEnable
```