---
type: concept
title: 产品编码 productCode
page_key: concepts/product_code
domain: 外部渠道与银行对接
status: draft
aliases:
  - productCode
  - platformProductCode
  - ProductCodeEnum.ACFLOW
  - refPlatformProductCode
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValue
  - code:ProjectAlipayClearingConfigApplication#isAlipayClearingConfigured
  - code:CpcnBankProviderImpl#listXylCustAccountBanks
contract_version: "0.1"
maps_to: "平台产品编码；RPC 路由（RpcAppVo.productAppId）与清分默认产品均以此为键，代码中默认值恒为 ACFLOW"
adjudication: synonym
boundary: "productCode 是编码字符串，platformProductId 是主键 ID；validateSetValue 中由 project→TenantProductDO→PlatformProductDO→pp.getCode()/getProductCode() 逐级解析，两者不可混用"
also_confused_with:
  - tenantProductId（租户产品主键）
  - platformProductId（平台产品主键）
---

# 产品编码 productCode

## 业务定位

`productCode` 是平台产品编码字符串，在渠道与银行对接链路中承担两类键值：RPC 路由（`RpcAppVo.productAppId`）与清分产品选择。代码中默认值恒为 `ACFLOW`，相关口径见 [[calibers/alipay_clearing_default_product]]（入参为空时兜底 `ACFLOW`）与 [[calibers/bocom_clearing_product]]（交e保按配置集合逐产品查询）。

## 需求背景

银行账户查询、清分配置、RPC 路由都要求以"产品"为维度隔离数据：同一企业在不同产品下的账户与配置互不相同（见 [[calibers/bocom_account_existence]] 中同时限定 `platformCode` 与 `productCode`）。因此需要一个稳定的编码字符串在各系统间传递，`ACFLOW` 被当作缺省产品。

## 边界澄清

`productCode`（编码字符串）与 `tenantProductId`（租户产品主键）、`platformProductId`（平台产品主键）不可混用。`validateSetValue` 中通过 project → `TenantProductDO` → `PlatformProductDO` 再取 `pp.getCode()` / `getProductCode()` 逐级解析得到编码，说明主键与编码之间是多级映射关系。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 口径：[[calibers/bocom_clearing_product]]、[[calibers/alipay_clearing_default_product]]、[[calibers/bocom_account_existence]]
- 载体表：[[tables/cust_company_info]]
- 概念：[[concepts/channel]]