---
type: rule
title: 变更流程重建
page_key: change_rebuild
domain: 企业变更与运营变更
status: draft
aliases: [changeRebuild, 变更重建/拒绝旧流程]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: rules
---

规则内容：取该企业最新一条 `status` 非 `CUST_CHECK_PASS`/`CUST_CHECK_REJECT` 的变更记录（[[rebuildable_change_process]]）；不存在则抛「无变更流程，不支持拒绝」；存在则调用运营中台 `changeRejectProcess` 结束旧流程并由客户重新发起；且 `companyId` 必须等于当前登录企业，构成越权校验。

## 需求背景

同一企业只允许存在一条在途变更。客户重新发起时，平台需要先结束旧流程再建新流程，同时防止跨企业操作他人流程。

## 版本演进

v0.1：首次固化，含越权校验要求。

```ground:rule
name: 变更流程重建
content: "取该企业最新一条 status 非 CUST_CHECK_PASS/CUST_CHECK_REJECT 的变更记录；不存在则抛'无变更流程，不支持拒绝'；存在则调用运营中台 changeRejectProcess 结束旧流程并由客户重新发起；且 companyId 必须等于当前登录企业"
impact: 拒绝旧流程、重建新流程；越权校验
field_targets:
  - cust_change_record.cust_id
  - cust_change_record.status
  - cust_change_record.oper_cust_id
evidence: "code_path:CustChangeApplication.java#changeRebuild"
```

相关页面：[[rebuildable_change_process]]、[[cust_change_record_status]]、[[cust_id]]、[[cust_change_record]]。