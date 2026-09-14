---
type: caliber
title: 企业可发起变更
page_key: company-change-enable
domain: 企业变更与运营变更
status: draft
aliases: [变更入口可用性, changeEnable]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeEnable
contract_version: "0.1"
belong: calibers
---

「企业可发起变更」是变更入口的可用性口径：企业准入审核状态不等于 `CUST_CHECK_CHECKING` 时才允许发起变更。字段语义见 [[tables.cust_company_info]]，与变更单状态 [[concepts.change-status]] 的边界见该概念页；落地规则见 [[rules.change-application-admission]]。

## 需求背景

企业准入审核在途时，企业主体信息本身可能还在变化，此时不允许叠加变更申请，避免同一企业出现两条互相冲突的审批链路。该口径是企业不存在时同样返回不可用的前置校验。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.changeEnable`。

```ground:caliber
name: 企业可发起变更
predicate: "cust_company_info.check_status <> 'CUST_CHECK_CHECKING'"
scope: 变更入口可用性校验
evidence: code_path:CustChangeApplication.java:changeEnable
```