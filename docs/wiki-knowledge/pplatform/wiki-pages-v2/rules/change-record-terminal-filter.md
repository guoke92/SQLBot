---
type: rule
title: 变更单终态过滤
page_key: rule.change-record-terminal-filter
domain: 企业变更与运营变更
status: draft
aliases: [终态过滤, notIn 终态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

`CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 视为终态，取在途变更单时用 notIn 排除。口径见 [[calibers.change-record-terminal-status]]，状态全集见 [[processes.cust-change-record-status]]，该过滤是流程重建 [[rules.change-rebuild]] 的前置步骤。

## 需求背景

企业可以多次发起变更，历史已完结单据必须与在途单据区分开；以终态集合做反向过滤比枚举在途状态更稳妥，新增中间态时不需要改判据。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeRebuild`。

```ground:rule
name: 变更单终态过滤
content: CUST_CHECK_PASS / CUST_CHECK_REJECT 视为终态，取在途变更单时用 notIn 排除
impact: 流程重建与在途判断的基础口径
field_targets:
  - cust_change_record.status
evidence: code_path:CustChangeApplication.java:changeRebuild
```