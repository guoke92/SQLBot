---
type: rule
title: 变更在途判定（企业维度）
page_key: change-on-way-company
domain: 企业变更与运营变更
status: draft
aliases: [在途变更规则, changeHasBusiOnWay]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeHasBusiOnWay
contract_version: "0.1"
belong: rules
---

企业 [[tables.cust_company_info]] 的 `cust_status='CHANGE'` 即视为存在在途变更业务，`changeHasBusiOnWay` 返回 true。该判定决定变更入口是否可用以及页面跳转是否走运营中台变更待办页，口径见 [[calibers.company-change-on-way]]，状态来源见 [[processes.cust-company-info-status]]。

## 需求背景

变更审批在运营中台执行，平台侧需要低成本判断「企业是否有事在办」，因此选择企业生命周期状态这一结果态作为判据，而不是聚合 [[tables.cust_change_record]] 集合。与准入校验 [[rules.change-application-admission]] 互为补充：一个看企业状态，一个看准入审核状态。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeHasBusiOnWay`。

```ground:rule
name: 变更在途判定（企业维度）
content: 企业 cust_status='CHANGE' 即视为存在在途变更业务，changeHasBusiOnWay 返回 true
impact: 决定变更入口是否可用、页面跳转是否走运营中台变更待办页
field_targets:
  - cust_company_info.cust_status
evidence: code_path:CustChangeApplication.java:changeHasBusiOnWay
```