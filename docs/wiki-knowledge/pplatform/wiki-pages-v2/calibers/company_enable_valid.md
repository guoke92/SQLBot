---
type: caliber
title: 有效企业主数据
page_key: company_enable_valid
domain: CA证书收费
status: draft
aliases:
  - enable = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
belong: calibers
---

有效企业主数据口径限定 [[ca_fee_company]] 中 `enable = 'Y'` 的行，用于台账查询、规则引擎评估与企业快照读取。所有企业维度的统计与判定都应先经过本口径，避免把历史失效行纳入计算。

## 需求背景

企业主数据存在失效（关闭／合并等）场景，需要在查询入口统一过滤，保证台账口径与规则结论一致。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 有效企业主数据
predicate: ca_fee_company.enable = 'Y'
scope: 台账查询、规则引擎、企业快照
evidence: CaFeeLedgerQueryService.java
```