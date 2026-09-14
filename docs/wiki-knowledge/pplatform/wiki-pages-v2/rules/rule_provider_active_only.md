---
type: rule
title: 对外规则查询只暴露已生效规则
page_key: rule_provider_active_only
domain: 资金规则与异常处理
status: draft
aliases:
  - Provider 只查 ACTIVE
  - 规则三组聚合
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java
  - db:funding_rule_info
  - db:funding_rule_detail
  - reqdoc:funding-rule-active-only-query
contract_version: "0.1"
belong: rules
---

对外查询按 fundingPartyMark + productCode + ruleStatus=ACTIVE 取头表，无生效规则返回 null；再按 ruleInfoId + enable='Y' 取明细，按 ruleLayer 分组为 UNDERLYING / FINANCING / OTHER 返回。

## 需求背景

需求侧主张与实现一致：资方规则查询按 fundingPartyMark + productCode 只取 ACTIVE 规则并聚合为底层/融资/其他三组（code_status: confirmed）。因此 PENDING / INACTIVE 规则对外不可见，配置完成到对外生效必须显式调用 activeRule（[[funding_rule_status_machine]]）。

## 版本演进

v0 首次建立，锚点 evidence 采用双源：代码路径 + 需求文档主张 slug。

```ground:rule
name: 对外规则查询只暴露已生效规则
content: FundingPartyRuleProviderImpl 按 fundingPartyMark + productCode + ruleStatus=ACTIVE 查询，无生效规则返回 null；再按 ruleInfoId + enable='Y' 查明细，按 ruleLayer 分组为 UNDERLYING/FINANCING/OTHER。
impact: PENDING/INACTIVE 规则对外不可见
field_targets:
  - funding_rule_info.rule_status
  - funding_rule_detail.rule_layer
evidence: code_path:FundingPartyRuleProviderImpl.java:doQuery + reqdoc:funding-rule-active-only-query
```