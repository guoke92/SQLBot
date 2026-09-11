---
type: process
title: 客户互通产品开通状态流转
page_key: processes/interworking_product_open_status
domain: 互通产品
status: draft
aliases: [互通产品开通状态, cust_interworking_product.open_status]
oid: 1
scope:
  databases: []
sources:
  - code:TenantInterworkingProductApplication
  - db:cust_interworking_product
contract_version: "0.1"
---

客户互通产品开通状态位于 [[tables/cust_interworking_product]] 的 open_status 列，配置侧在 [[tables/tenant_interworking_product]]。开通由 active 完成；取消由 cancel 完成，且一旦关联项目即不允许取消（见 [[rules/interworking_product_cancel_guard]]）。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决的是互通产品在客户维度的开关管理，并对取消动作加上「已关联项目」这一前置限制。

## 版本演进
- 状态值 DB 侧为 OPENED，代码侧另有 OPENING，二者命名体系与租户产品的 N/P/Y 不同，见 [[concepts/product_open_status]]。
- 语义分析中 cancel 迁移的代码路径证据被截断，本页只登记有完整证据的 active 迁移，cancel 相关约束单列于规则页并标注待复核。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 客户互通产品开通状态
field: cust_interworking_product.open_status
states:
  - value: OPENED
    label: 已开通
    source: db_dist
  - value: OPENING
    label: 开通中
    source: code_enum
transitions:
  - from: 未开通
    event: TenantInterworkingProductApplication.active 开通互通产品
    to: OPENED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantInterworkingProductApplication.java:active"
```