---
type: caliber
title: 支付宝清分默认产品口径
page_key: alipay_clearing_default_product
domain: 外部渠道与银行对接
status: draft
aliases:
  - 支付宝清分默认产品口径
  - 支付宝清分兜底 ACFLOW
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectAlipayClearingConfigApplication#isAlipayClearingConfigured
  - code:ClientProjectAlipayClearingConfigSyncService#getAppId
contract_version: "0.1"
belong: calibers
---

# 支付宝清分默认产品口径

## 业务定位

该口径规定：在判断项目是否已配置支付宝清分、以及获取 `appId` 时，若产品编码入参为空，则用 `ACFLOW` 兜底。相同口径同时出现在 `ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured` 与 `ClientProjectAlipayClearingConfigSyncService.getAppId` 两处，须保持一致。

## 需求背景

支付宝渠道的清分配置是按项目+产品维度维护的，调用方在老项目中可能不传 `productCode`；为避免因缺参导致"未配置"误判，代码统一以 `ACFLOW` 作为默认产品。该默认值与交e保侧的缺省集合 [[calibers/bocom_clearing_product]] 的首项一致，二者共同把 `ACFLOW` 定位为默认清分产品（语义见 [[concepts/product_code]]）。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 支付宝清分默认产品口径
predicate: "productCode = 'ACFLOW'（入参为空时兜底）"
scope: ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured；ClientProjectAlipayClearingConfigSyncService.getAppId 同口径
evidence: "code:ProjectAlipayClearingConfigApplication#isAlipayClearingConfigured"
```

## 关联页面

- 相关口径：[[calibers/bocom_clearing_product]]、[[calibers/bocom_account_existence]]
- 术语：[[concepts/product_code]]
- 载体表：[[tables/cust_company_info]]