---
type: rule
title: 异常解析导入-全量校验通过才入库
page_key: rules/exception_import_all_or_nothing
domain: funding
status: draft
aliases:
  - 异常解析导入原子性
  - all-or-nothing 导入
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#importRecords"
contract_version: "0.1"
---

# 异常解析导入-全量校验通过才入库

## 业务定位

异常解析导入依次执行四阶段校验——行级必填、`productCode` 枚举、对接方标识存在性、唯一键重复；**任一阶段产生错误即返回错误列表且不写库**。这保证批量导入的原子性，避免「一半成功一半失败」导致运营无法判断最终状态。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。与之配套的还有 [[rules/exception_import_row_limit_5000]] 的规模上限。

```ground:rule
rule: 异常解析导入-全量校验通过才入库
content: "导入依次执行行级必填、productCode 枚举、对接方标识存在性、唯一键重复校验；任一阶段产生错误则返回错误列表且不写库（all-or-nothing）"
impact: "保证批量导入原子性，避免半量写入"
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: "code:ExceptionResolutionApplication#importRecords"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_import_rpc_group_by_product]]、[[rules/exception_unique_key_dedup]]、[[rules/exception_upsert_write]]