---
type: rule
title: 流程重建（重新发起变更）
page_key: rule.change-rebuild
domain: 企业变更与运营变更
status: draft
aliases: [changeRebuild, 重新发起变更]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

流程重建取该企业最新一条非终态变更记录（过滤口径见 [[rules.change-record-terminal-filter]]），通过运营中台接口结束旧流程（备注：客户操作重新发起，拒绝旧流程），随后允许发起新流程；操作人须为当前企业，否则抛无权限。涉及字段见 [[tables.cust_change_record]]，终态判定见 [[processes.cust-change-record-status]] 中「重新发起」迁移与 [[calibers.change-record-terminal-status]]。

## 需求背景

客户在上一笔变更未走完时再次进入变更入口，需要「以新替旧」而不是并存两条在途流程；因此先结束旧流程，再放行新流程，保证同一企业同一时刻只有一条在途单。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeRebuild`。

```ground:rule
name: 流程重建（重新发起变更）
content: 取该企业最新一条非终态变更记录，通过运营中台接口结束旧流程（备注：客户操作重新发起，拒绝旧流程），随后允许发起新流程；操作人须为当前企业，否则抛无权限
impact: 同一企业可存在多次变更发起，旧单被拒结
field_targets:
  - cust_change_record.status
  - cust_change_record.oper_cust_id
  - cust_change_record.cust_id
evidence: code_path:CustChangeApplication.java:changeRebuild
```