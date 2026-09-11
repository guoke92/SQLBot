---
type: caliber
title: 变更单终态
page_key: caliber.change-record-terminal-status
domain: 企业变更与运营变更
status: draft
aliases: [变更终态口径, 非终态变更单]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

「变更单终态」是 [[tables.cust_change_record]] 上用于识别企业是否存在未完结变更流程的口径：`CUST_CHECK_PASS` 与 `CUST_CHECK_REJECT` 视为终态，取在途变更单时以 notIn 排除，取最新一条非终态记录用于流程重建。状态取值全集见 [[processes.cust-change-record-status]]，应用规则见 [[rules.change-record-terminal-filter]] 与 [[rules.change-rebuild]]。注意本口径只描述变更单维度，与企业生命周期状态 [[calibers.company-change-on-way]] 不同层。

## 需求背景

流程重建要求「同一企业同一时刻只保留一条在途变更单」，因此必须有一个稳定的终态集合把已完结单据排除在外。终态的写入由运营中台回调链路负责，本地模块只读该口径，见 [[rules.audit-callback-dispatch]]。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.changeRebuild` 的查询条件。

```ground:caliber
name: 变更单终态
predicate: "cust_change_record.status IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')"
scope: 识别企业是否存在未完结变更流程
evidence: code_path:CustChangeApplication.java:changeRebuild（notIn PASS/REJECT 取最新一条）
```