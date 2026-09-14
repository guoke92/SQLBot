---
type: rule
title: 产品类型编码数组的 LIKE 筛选与白名单校验
page_key: product-type-arr-like-filter
domain: 微企链立项与项目审批
status: draft
aliases:
  - product_type_arr LIKE 筛选
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: rules
---

由于产品类型以 JSON 数组字符串存放，筛选无法用等值匹配，只能用 `LIKE '%"code"%'` 在数组文本里找编码。为避免注入与脏值，拼接前会先经过枚举白名单校验。

运维上要注意两点：该匹配是子串匹配，编码之间存在包含关系时可能误命中；白名单外的编码无法被筛出。字段的双表示见 [[concepts/product-type-coding]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 产品类型编码数组的 LIKE 筛选与白名单校验
subject: wechat_project_approval_apply.product_type_arr
evidence: code
source_meaning: 产品类型编码 JSON 数组，筛选用 LIKE '%"code"%'（先经枚举白名单校验）
```