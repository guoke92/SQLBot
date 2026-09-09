---
type: rule
title: 异常解析导入重复检测
page_key: exception_resolution_import_duplicate_detection
belong: rules
domain: 资金方规则与异常解决
status: published
aliases:
  - 导入重复检测
oid: 1

sources:
  - code:ExceptionResolutionApplication.collectFundingPartyCodeErrors
contract_version: "0.1"
field_targets: [funding_exception_resolution.error_keyword, funding_exception_resolution.funding_party_code, funding_exception_resolution.product_code]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束 [[funding_exception_resolution]] 表的导入查重行为。导入时按 productCode + fundingPartyCode + errorKeyword 查询已存在记录；若存在则报错“异常解析配置信息已存在”，导致整批导入失败，而不是更新。

## 需求背景

该规则与 [[exception_resolution_unique_key]] 口径一致，但实际行为与类注释的 upsert 描述矛盾：重复导入会被阻止而不是更新。这是导入流程的重要约束。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "异常解析导入重复检测"
content: "导入时按 (productCode + fundingPartyCode + errorKeyword) 查询已存在记录；若存在则报错“异常解析配置信息已存在”，导致整批导入失败，而不是更新。"
impact: "实际行为与类注释的 upsert 描述矛盾；重复导入会被阻止。"
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: "code:ExceptionResolutionApplication.collectFundingPartyCodeErrors 末尾 existingMap 检查"
```