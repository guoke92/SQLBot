---
type: rule
title: 互通产品取消开通前置约束
page_key: interworking_product_cancel_guard
domain: 互通产品
status: draft
aliases: [不允许取消开通, 互通产品取消]
oid: 1
scope:
  databases: []
sources:
  - code:TenantInterworkingProductApplication
contract_version: "0.1"
belong: rules
---

该规则约束 [[tables/cust_interworking_product]] 的取消动作：一旦互通产品已被项目关联，就不允许取消开通。它是 [[processes/interworking_product_open_status]] 中 OPENED → 未开通 迁移的前置条件。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则存在的目的是避免已投产项目失去其产品配置。

## 版本演进
本次语义分析中该迁移的代码路径证据被截断，规则文本来自迁移描述；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 互通产品关联项目后不允许取消开通
table: cust_interworking_product
fields: [open_status]
statement: TenantInterworkingProductApplication.cancel 取消开通，关联项目后不允许取消
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/[证据截断]/TenantInterworkingProductApplication.java:cancel"
```