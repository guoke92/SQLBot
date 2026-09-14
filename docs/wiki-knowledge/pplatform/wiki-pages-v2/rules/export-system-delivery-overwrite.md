---
type: rule
title: 导出时 system_delivery 被产品类型覆盖
page_key: export-system-delivery-overwrite
domain: 微企链立项与项目审批
status: draft
aliases:
  - 导出覆盖交付方式列
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
belong: rules
---

在导出流程中，`system_delivery` 这一列会被 `product_type_arr` 翻译出的中文覆盖写入。也就是说导出文件里这一列的内容并非库内该列的原值，而是产品类型的中文。

这条规则与统计页把该列当交付范围过滤的用法直接冲突，是全主题最容易误读的一处，概念层面的说明见 [[concepts/system-delivery-reuse]]、[[concepts/product-type-coding]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该覆盖行为属历史遗留复用，本次无文档主张可佐证其引入时间。

```ground:rule
rule: 导出时 system_delivery 被产品类型覆盖
subject: wechat_project_approval_apply.system_delivery
evidence: code
source_meaning: DB 注释为『系统交付方式』，但统计页用它做交付范围过滤（SaaS/Saas+本地化），导出时该列又被 product_type_arr 的中文覆盖写入，属被复用列
```