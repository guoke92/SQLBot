---
type: concept
title: 冻结
page_key: freeze
domain: 企业建档与认证
status: draft
aliases:
  - FREEZE
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:freeze
  - code_path:CustCompanyInfoApplication.java:unfreeze
contract_version: "0.1"
maps_to: cust_company_info.cust_status
field_targets:
  - cust_company_info.cust_status
  - cust_status.FREEZE
adjudication: synonym
also_confused_with: []
belong: concepts
field_targets: [cust_company_info.cust_status]
sources: ["enrich:wiki-admin"]
---

"冻结"表示企业主体被暂停使用：`cust_status` 由 `EFFECT` 置为 `FREEZE`，解冻则由 `FREEZE` 回到 `EFFECT`。冻结企业时会同时冻结企业管理员，且状态变更会同步业务系统，见 [[rules/cust_status_sync_third_party]]。

## 边界与歧义

业务叙述中的"违规冻结"即此动作；与注销的区别在于可逆——解冻后企业回到生效态，而 [[concepts/writeoff]] 不可逆。

## 需求背景

需求文档主张"已通过 → 已冻结"（anchor，双源：code_path:CustCompanyInfoApplication.java:freeze:custStatusOperator + reqdoc:已通过转已冻结或已注销），代码在 `custStatusOperator` 中以 `allowStatusList` 校验前置状态。

## 版本演进

v0 初稿：以冻结/解冻写值点为准。冻结是否影响在途流程的处理，待复核。

关联：[[concepts/writeoff]]、[[processes/cust_status_state_machine]]、[[calibers/effect_company_scope]]。

相关：[[cust_company_info]]
