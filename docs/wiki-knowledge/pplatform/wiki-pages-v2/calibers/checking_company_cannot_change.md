---
type: caliber
title: 审核中企业不可发起变更
page_key: checking_company_cannot_change
domain: 企业变更与运营变更
status: draft
aliases: [准入审核中不可变更, check_status=CUST_CHECK_CHECKING]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：`cust_company_info.check_status = 'CUST_CHECK_CHECKING'` 时不允许发起变更，是 [[change_precheck]] 规则的核心判定。

注意该口径只覆盖准入审核中一种情况；文档还主张「已冻结/已注销不允许变更」，代码未覆盖，见 [[change_precheck]] 的版本演进。

## 需求背景

企业准入审核与信息变更会互相改写同一批资质字段，准入审核中再叠加变更会造成两端状态冲突，因此前置拦截。

## 版本演进

v0.1：首次固化该口径，并标注其覆盖范围小于文档主张。

```ground:caliber
name: 审核中企业不可发起变更
predicate: "cust_company_info.check_status = 'CUST_CHECK_CHECKING'"
scope: 是否可变更申请校验
evidence: "code_path:CustChangeApplication.java#changeEnable"
```

相关页面：[[change_precheck]]、[[cust_company_info]]、[[change_status]]、[[change_on_way]]。