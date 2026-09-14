---
type: caliber
title: 可重建的变更流程
page_key: rebuildable_change_process
domain: 企业变更与运营变更
status: draft
aliases: [非终态变更流程, 可重建流程口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：可被流程重建逻辑命中的变更记录，是 `status NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')` 的记录。命中后取最新一条非终态记录，调用运营中台 `changeRejectProcess` 结束旧流程，由客户重新发起，见 [[change_rebuild]]。

## 需求背景

客户在流程未结束时重新发起变更，需要先收敛旧流程，避免同一企业存在多条在途变更；因此以「非终态」而非「审核中」为条件，把退回补充等中间态一并纳入。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 可重建的变更流程
predicate: "cust_change_record.status NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')"
scope: 变更流程重建前置条件
evidence: "code_path:CustChangeApplication.java#changeRebuild(notIn CheckStatus.PASS/REJECT)"
```

相关页面：[[change_rebuild]]、[[cust_change_record_status]]、[[cust_change_record]]、[[valid_change_record]]。