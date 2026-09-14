---
type: caliber
title: 企业在途变更
page_key: company-change-on-way
domain: 企业变更与运营变更
status: draft
aliases: [在途变更口径, changeHasBusiOnWay]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeHasBusiOnWay
  - code_path:CustChangeApplication.java:getRedirectPage
contract_version: "0.1"
belong: calibers
---

「企业在途变更」以 [[tables.cust_company_info]] 的 `cust_status = 'CHANGE'` 判定：命中即认为企业存在在途变更业务，`changeHasBusiOnWay` 返回 true。该口径同时影响变更入口可用性与页面跳转（是否进入运营中台变更待办页）。生命周期状态机见 [[processes.cust-company-info-status]]，落地规则见 [[rules.change-on-way-company]]；与单张变更单的终态口径 [[calibers.change-record-terminal-status]] 互补：前者是结果态，后者是单据集合。

## 需求背景

变更审批在运营中台进行，平台侧需要在用户进入时快速判断「是否有事正在办」，因此选择一个单字段的结果态作为在途标识，而不是每次聚合变更单集合。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.changeHasBusiOnWay` / `getRedirectPage`。

```ground:caliber
name: 企业在途变更
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: 变更在途判定与页面跳转
evidence: code_path:CustChangeApplication.java:changeHasBusiOnWay / getRedirectPage
```