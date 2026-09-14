---
type: rule
title: 产品路由默认 ACFLOW
page_key: default_product_route_acflow
domain: 外部渠道与银行对接
status: draft
aliases:
  - 默认产品码 ACFLOW
  - allowedProductCodes
oid: 1
scope:
  databases:
    - cust
sources:
  - code:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured
  - code:ClientProjectAlipayClearingConfigSyncService.getAppId
  - code:BocomQueryAccountByXylClientService.getAppId
  - code:CpcnBankProviderImpl.allowedProductCodes
contract_version: "0.1"
belong: rules
---

清分相关查询在 productCode 为空时按 ACFLOW 兜底；交e保清分银行卡查询的允许产品由 Nacos 配置 `bocom.clearing.allowedProductCodes` 控制，默认 ACFLOW、RVSFACTOR_PC。

## 需求背景
渠道请求常不带产品维度，缺省兜底保证路由可预测；配置化白名单则允许运营在不发版的前提下调整可查产品范围。业务背景见 [[clearing]]，回填落点见 [[cust_account_info]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 产品路由默认 ACFLOW
content: 支付宝清分配置查询 productCode 为空时默认 ACFLOW；交e保清分银行卡查询的允许产品为 Nacos 配置 bocom.clearing.allowedProductCodes(默认 ACFLOW,RVSFACTOR_PC)
impact: 渠道请求的产品维度与 RpcAppVo 路由
field_targets: []
evidence: "code:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured; ClientProjectAlipayClearingConfigSyncService.getAppId; BocomQueryAccountByXylClientService.getAppId; CpcnBankProviderImpl.allowedProductCodes"
```