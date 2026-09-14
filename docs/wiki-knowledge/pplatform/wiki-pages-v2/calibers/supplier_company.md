---
type: caliber
title: 供应商企业
page_key: supplier_company
domain: 租户配置
status: draft
aliases:
  - 供应商企业
  - SUPPLIER
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/AssetOperatorSyncApplication.java:syncAssetOperator
contract_version: "0.1"
belong: calibers
---

在企业类型为 `SUPPLIER` 的范围内，资产审核运营人员的同步才生效；非供应商企业不参与该同步。该口径限定运营人员同步的作用域，避免把审核运营人写到不相关的企业上。

## 需求背景

资产审核的运营人归属只对供应商企业有业务意义，因此同步任务在入口处按企业类型裁剪数据集。

## 版本演进

v0.1：依据 `syncAssetOperator` 的企业类型过滤建立口径。

```yaml
caliber: 供应商企业
predicate: "cust_company_info.cust_company_type = 'SUPPLIER'"
scope: 资产审核运营人员同步仅对供应商生效
evidence: "code:AssetOperatorSyncApplication.java:syncAssetOperator"
```

相关页面：[[concepts/tenant_operator]]、[[concepts/op_contact_a]]。