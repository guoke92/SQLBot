---
type: concept
title: system_delivery 复用列
page_key: concept/system-delivery-reuse
domain: 微企链立项与项目审批
status: draft
aliases:
  - 系统交付方式
  - system_delivery
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.system_delivery
field_targets:
  - table: wechat_project_approval_apply
    field: system_delivery
adjudication: 该列 DB 注释为『系统交付方式』，但在统计页被用作交付范围过滤（SaaS/Saas+本地化），在导出时又被 product_type_arr 的中文覆盖写入。一列承担三种语义，读该列前必须先确认上下文。
also_confused_with:
  - wechat_project_approval_apply.product_type（产品类型中文 CSV，导出会写到 system_delivery）
sources: ["enrich:wiki-admin"]
---

这是一条典型的「列语义漂移」：注释、统计过滤、导出写入三者说法不一致。因为导出会覆盖写入，所以从导出文件里看到的 `system_delivery` 未必是统计页过滤所依据的那个值。

处理此类字段的原则是先锁定读它的代码路径（统计过滤 vs 导出），再判断取值含义；不要依赖 DB 注释（见 [[rules/export-system-delivery-overwrite]]）。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该列被复用的现状属历史遗留，本次无文档主张可佐证其变更时间。

相关页面：[[tables/wechat_project_approval_apply]]、[[concepts/product-type-coding]]。

相关：[[wechat_project_approval_apply]]
