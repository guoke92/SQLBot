---
type: concept
title: 产品 code
page_key: product_code
domain: 资金方规则与异常解决
status: published
aliases:
  - productCode
  - product_code
oid: 1

sources:
  - db:funding_exception_resolution
  - db:funding_rule_info
  - db:funding_rule_front_cfg
  - db:funding_rule_detail
maps_to: "funding_exception_resolution.product_code / funding_rule_info.product_code / funding_rule_front_cfg.product_code / funding_rule_detail.product_code"
field_targets:
  - funding_exception_resolution.product_code
  - funding_rule_info.product_code
  - funding_rule_front_cfg.product_code
  - funding_rule_detail.product_code
adjudication: "synonym"
also_confused_with: []
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

产品 code 是资金方规则与异常解决领域中的维度概念，用于区分业务产品（如 ACFLOW、RVSFACTOR_PC），取值来自 ProductCodeEnum。该概念在 [[funding_exception_resolution]]、[[funding_rule_info]]、[[funding_rule_front_cfg]]、[[funding_rule_detail]] 四张表中字段名均为 product_code。

## 需求背景

产品 code 是规则和异常解析配置的顶级维度，与 [[funding_party_identifier]] 组合形成业务主语。导入校验时需要进行 productCode 枚举校验（参见 [[exception_resolution_import_all_or_nothing]]），并且是 [[exception_resolution_unique_key]] 和 [[funding_rule_create_duplicate_check]] 的组成部分。

## 版本演进

边界说明：同一概念在不同表字段名一致，均为 product_code。当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。