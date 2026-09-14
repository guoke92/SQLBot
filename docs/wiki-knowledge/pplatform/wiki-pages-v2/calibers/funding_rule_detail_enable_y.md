---
type: caliber
title: 资方规则明细有效数据口径
page_key: funding_rule_detail_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则明细 enable 口径
  - funding_rule_detail enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java
contract_version: "0.1"
belong: calibers
---

[[funding_rule_detail]] 的详情查询与 Provider 查询均以 enable='Y' 为口径，saveRuleInfo 写明细时固定写 'Y'。

## 需求背景

明细更新逻辑依赖本口径判存：命中已有 enable='Y' 明细才更新、否则新增，所以 enable 的写入一致性直接决定明细是否会被重复插入，见 [[rule_save_version_detail_sync]]。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 资方规则明细有效数据
predicate: funding_rule_detail.enable = 'Y'
scope: 详情/Provider 查询过滤；saveRuleInfo 固定写 Y
evidence: code
```