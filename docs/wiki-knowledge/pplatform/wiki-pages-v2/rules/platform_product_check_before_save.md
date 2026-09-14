---
type: rule
title: 平台产品保存前置校验
page_key: platform_product_check_before_save
domain: 资金规则与异常处理
status: draft
aliases:
  - BR-001
  - PlatformProductApplication.checkBeforeSave
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/PlatformProductApplication.java
  - reqdoc:BR-001
contract_version: "0.1"
belong: rules
---

平台产品保存前调用 checkBeforeSave，校验产品 code 唯一性与类型枚举等，失败抛 BaseException 阻断保存。该规则是异常解析与规则导入中「产品 code 合法集合」的上游来源（[[exception_import_name_code_translation]]，listPlatformProduct(GENERAL)）。

## 需求背景

本主题需求文档中仅有产品与项目管理文档提及平台产品校验与列表过滤，**未对资金规则与异常处理主题给出独立业务规则章节**（document_claim，未证实）。与产品列表过滤相关的主张（BR-002）在代码中未见实现，见 REVIEW 记录。

## 版本演进

v0 首次建立，来源为需求文档主张 action=anchor（code_status: confirmed），锚点 evidence 写双源。

```ground:rule
name: 平台产品保存前置校验
content: 调用 PlatformProductApplication.checkBeforeSave 校验产品 code 唯一性、类型枚举等，失败抛 BaseException 阻断保存（BR-001）。
impact: 产品 code 重复或类型不合法时保存被阻断；产品合法集合是下游导入校验（异常解析、资方规则）的前置依赖
field_targets: []
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/PlatformProductApplication.java:checkBeforeSave + reqdoc:BR-001
```