---
type: concept
title: 资金方名称（fundingPartyName）
page_key: funding_party_name
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方名称
  - fundingPartyName
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_exception_resolution
  - db:funding_rule_info
maps_to: funding_exception_resolution.funding_party_name
field_targets:
  - funding_exception_resolution.funding_party_name
  - funding_rule_info.funding_party_name
adjudication: synonym
also_confused_with:
  - funding_rule_info.funding_party_name
contract_version: "0.1"
belong: concepts
field_targets: [funding_exception_resolution.funding_party_name]
sources: ["enrich:wiki-admin"]
---

资金方名称在两表中各自冗余存储，**均非关联键**，只服务于展示与模糊查询。查询请勿以名称作为 join 条件，关联一律使用资方标识（[[funding_party_mark]]）。

## 需求背景

- 异常解析导入必填资金方名称列，并参与「资金方名称-标识」→ fundingKey 的翻译（[[exception_import_name_code_translation]]）。
- 规则导入时名称来自资方 RPC 的 mark→name 映射；由于校验产品硬编码为 ACFLOW，落库名称可能取自 ACFLOW 映射（[[rule_import_funding_party_hardcoded]]）；更新规则时名称会被覆盖写（[[rule_save_version_detail_sync]]）。

## 版本演进

v0 首次建立，判定类型 synonym：两表同义字段，取值来源可能不同但语义一致。

相关：[[funding_exception_resolution]]
