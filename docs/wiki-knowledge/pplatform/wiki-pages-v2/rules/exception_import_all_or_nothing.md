---
type: rule
title: 异常解析导入全量校验通过才入库
page_key: exception_import_all_or_nothing
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析导入全量校验
  - 导入不做部分成功
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_exception_resolution
  - reqdoc:import-all-validate-before-save
contract_version: "0.1"
belong: rules
---

导入 [[funding_exception_resolution]] 时，系统先做行级必填校验，再做产品枚举比对，最后按 productCode 分组批量调 RPC 校验对接方标识并做唯一键查重。任一错误直接返回错误列表且不写库，只有全部通过才在单事务内写库。

## 需求背景

需求侧主张与实现一致：资源导入遵循「全量校验通过才入库；任一失败直接返回，不做任何保存/更新」（BR 级主张，code_status: confirmed）。因此导入的失败语义是「整批拒绝」而非「行级忽略」，使用方需按错误列表整批修正后重试。单次导入上限 5000 行。

## 版本演进

v0 首次建立，锚点 evidence 采用双源：代码路径 + 需求文档主张 slug。

```ground:rule
name: 异常解析导入全量校验通过才入库
content: 阶段1 Excel 行级必填校验（产品code/对接方标识/资金方名称/报错关键字/建议处理方案 5 列）→ 阶段2 productCode 枚举比对 → 阶段3 按 productCode 分组各调一次 RPC 校验对接方标识 + 唯一键 (productCode,fundingPartyCode,errorKeyword) 查重；任一错误直接返回错误列表且不写库；全部通过才在单事务内 saveOrUpdateBatch。
impact: 任何一行错误都会导致整批不落库；单次导入上限 5000 行
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: code_path:ExceptionResolutionApplication.java:importRecords/doUpsertAll + DB:funding_exception_resolution_un(funding_party_code,error_keyword,product_code) + reqdoc:import-all-validate-before-save
```