---
type: rule
title: 异常解析导入全量校验通过才入库
page_key: exception_resolution_import_all_or_nothing
domain: 资金方规则与异常解决
status: published
aliases:
  - 导入全量校验
oid: 1

sources:
  - code:ExceptionResolutionApplication.importRecords
contract_version: "0.1"
field_targets: [funding_exception_resolution.error_keyword, funding_exception_resolution.funding_party_code, funding_exception_resolution.funding_party_name, funding_exception_resolution.product_code, funding_exception_resolution.suggestion]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束 [[funding_exception_resolution]] 表的导入流程。导入时任何一阶段产生错误（文件读取必填校验、productCode 枚举校验、对接方标识 RPC 校验），整个批次都不会写入数据库，直接返回错误列表。

## 需求背景

异常解析配置数据质量要求高，部分成功写入可能导致数据不完整。该规则通过三阶段校验防止部分成功写入，保证数据完整性。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "异常解析导入全量校验通过才入库"
content: "导入流程分三阶段（文件读取必填校验、productCode 枚举校验、对接方标识 RPC 校验）；任一阶段产生错误，直接返回错误列表，不执行任何数据库写入。"
impact: "防止部分成功写入，保证数据完整性。"
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.funding_party_name
  - funding_exception_resolution.error_keyword
  - funding_exception_resolution.suggestion
evidence: "code:ExceptionResolutionApplication.importRecords 方法体"
```