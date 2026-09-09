---
type: rule
title: 可变更申请校验规则
page_key: rule_change_enable_check
belong: rules
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.changeEnable", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.check_status]
coverage_note: 企业
scope:
  databases: [lowcode_pplatform]
---

该规则在发起新变更申请前校验企业审核状态，如果企业正处于审核中（`check_status = CUST_CHECK_CHECKING`），则禁止再次提交，防止审核期间重复产生变更申请。

## 需求背景

暂无特定需求声明。

```ground:rule
name: "可变更申请校验规则"
content: "当企业 check_status 为 CUST_CHECK_CHECKING 时，changeEnable 返回 false，不允许发起新变更申请"
impact: "防止审核期间重复提交变更申请"
field_targets:
  - "cust_company_info.check_status"
evidence: "code_path:CustChangeApplication.changeEnable"
```

## 版本演进

暂无。

相关：[[cust_company_info]]
