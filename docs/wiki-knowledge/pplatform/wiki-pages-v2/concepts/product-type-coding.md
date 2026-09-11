---
type: concept
title: 产品类型双表示（编码数组与中文 CSV）
page_key: concept/product-type-coding
domain: 微企链立项与项目审批
status: draft
aliases:
  - product_type_arr
  - 产品类型编码
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.product_type_arr
  - wechat_project_approval_apply.product_type
field_targets:
  - table: wechat_project_approval_apply
    field: product_type_arr
  - table: wechat_project_approval_apply
    field: product_type
adjudication: 同一份产品类型信息在本表存两份——product_type_arr 是编码 JSON 数组（用于筛选），product_type 是中文名 CSV（由编码翻译而来，用于展示）。两者是一对翻译关系，不是两个独立的业务字段。
also_confused_with:
  - wechat_project_approval_apply.system_delivery（导出时会被产品类型中文覆盖写入的复用列，见 concepts/system-delivery-reuse）
sources: ["enrich:wiki-admin"]
---

筛选走编码、展示走中文，是本主题里「一物两存」的典型。筛选实现用 JSON 字符串的 `LIKE '%"code"%'` 匹配编码数组，并且会先做一次枚举白名单校验再拼条件（见 [[rules/product-type-arr-like-filter]]）。

由于导出流程还会把中文产品类型写进 `system_delivery` 列（见 [[rules/export-system-delivery-overwrite]]），在排查导出的产品类型列时要注意这一层覆盖关系。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[concepts/system-delivery-reuse]]。

相关：[[wechat_project_approval_apply]]
