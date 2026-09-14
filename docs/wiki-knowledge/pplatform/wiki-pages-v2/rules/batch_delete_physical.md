---
type: rule
title: 批量删除为物理删除
page_key: batch_delete_physical
domain: 资金规则与异常处理
status: draft
aliases:
  - 物理删除
  - removeByIds / removeBatchByIds
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
belong: rules
---

[[funding_exception_resolution]] 与 [[funding_rule_info]] 的批量删除均走 MyBatis-Plus 物理删除（removeByIds / removeBatchByIds），并非 enable='N' 的逻辑删除。

## 需求背景

该行为澄清了 enable 字段的职责边界：enable 只是有效数据口径（[[exception_resolution_enable_y]]、[[funding_rule_info_enable_y]]），不承担软删；删除不可恢复，且删除 `code` 被 [[funding_rule_detail]].fund_rule_code_ref 引用的规则头时需自行评估悬挂引用风险。

## 版本演进

v0 首次建立。

```ground:rule
name: 批量删除为物理删除
content: 异常解析 batchDelete 用 removeByIds、规则 batchDelete 用 removeBatchByIds，均非 enable='N' 逻辑删除。
impact: 删除不可恢复，且 enable 字段并不承担软删职责
field_targets:
  - funding_exception_resolution.enable
  - funding_rule_info.enable
evidence: code_path:ExceptionResolutionApplication.java:batchDelete / FundRuleInfoApplication.java:batchDelete
```