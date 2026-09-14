---
type: process
title: 资方规则状态机
page_key: funding_rule_status_machine
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则状态流转
  - rule_status 状态机
  - RuleStatusEnum
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
contract_version: "0.1"
belong: processes
---

资方规则以 [[funding_rule_info]].rule_status 表达生命周期。新建规则一律落在 PENDING，只有 ACTIVE 才对外可见（[[rule_provider_active_only]]），因此状态流转是「配置完成 → 对外生效」的唯一开关。

## 需求背景

状态仅由 saveRuleInfo 的写入与 activeRule / inActiveRule 两个动作驱动，动作本身不校验前置状态：INACTIVE 可被 activeRule 直接拉回 ACTIVE，PENDING 也可被 inActiveRule 直接置为 INACTIVE。这意味着「失效再启用」不产生新的版本语义，版本号只由 saveRuleInfo 更新路径自增（[[rule_save_version_detail_sync]]）。枚举值审计与 DB 权重校验受数据限制，见 REVIEW 记录。

## 版本演进

v0 首次建立，状态集合与三条流转证据取自 state_machines；新增态以 NEW 表示「尚未落库」，不作为存储取值。

```ground:process
name: 资方规则状态机
field: funding_rule_info.rule_status
states:
  - value: PENDING
    label: 待生效
    source: code_enum
  - value: ACTIVE
    label: 生效中
    source: code_enum
  - value: INACTIVE
    label: 已失效
    source: code_enum
transitions:
  - from: NEW
    event: saveRuleInfo 新增（ruleInfoId 为空）
    to: PENDING
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:380
  - from: PENDING
    event: activeRule
    to: ACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:296
  - from: ACTIVE
    event: inActiveRule
    to: INACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:311
  - from: INACTIVE
    event: activeRule（无前置状态校验，可回到生效）
    to: ACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:296
  - from: PENDING
    event: inActiveRule（无前置状态校验，可直接置为失效）
    to: INACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:311
```