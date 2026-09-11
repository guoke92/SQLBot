---
type: process
title: 租户产品开通状态流转
page_key: processes/tenant_product_open_status
domain: 租户产品
status: draft
aliases: [租户产品开通状态, tenant_product.open_status]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProductApplication
  - db:tenant_product
contract_version: "0.1"
---

租户产品开通是「平台产品下发到租户」的落地动作，其状态位于 [[tables/tenant_product]] 的 open_status 列。非 ACFLOW/ORDER 类产品一次置为已开通；ACFLOW/ORDER 类产品需等待多级回调，先停留在开通中。状态的三值语义见 [[concepts/product_open_status]]，其中 N 只在数据侧出现。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决两个问题：①不同产品线的开通是否需要多级回调；②重复开通请求的幂等（见 [[rules/activation_idempotency]]）。

## 版本演进
- 代码枚举 ProductOpenStatusEnum 只覆盖 Y/P，DB 实测还有 N，说明「未开通」态在代码基线中未显式建模。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: "N"
    label: 未开通/默认
    source: db_dist
  - value: "P"
    label: 开通中/等待多级回调
    source: code_enum
  - value: "Y"
    label: 已开通
    source: code_enum
transitions:
  - from: "N"
    event: activeAndNotify 非 ACFLOW/ORDER 产品主动开通
    to: "Y"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: "N"
    event: activeAndNotify 产品为 ACFLOW/ORDER，先置为开通中等待多级回调
    to: "P"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: "Y"
    event: activeAndNotify 幂等命中已开通直接返回
    to: "Y"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
```