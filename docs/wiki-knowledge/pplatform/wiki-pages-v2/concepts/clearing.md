---
type: concept
title: 清分
page_key: clearing
domain: 外部渠道与银行对接
status: draft
aliases:
  - clearing
  - 交e保
  - 中金CFCA
  - 支付宝清分
  - 清分会员登记簿
oid: 1
scope:
  databases:
    - cust
sources:
  - code:AlipayClearingProvider
  - code:PayProvider
  - code:ICpcnApi
  - code:CpcnBankProviderImpl
contract_version: "0.1"
maps_to: cust_account_info.account_no
also_confused_with:
  - cust_company_info.company_ext_data
adjudication: boundary
belong: concepts
field_targets: [cust_account_info.account_no]
---

「清分」在本主题中是对接银行/清分渠道的一类能力集合，三条链路各自独立：支付宝清分走 AlipayClearingProvider（registry=alipay），交e保走 PayProvider/ClearingProvider（registry=clearing），中金走 ICpcnApi。

## 需求背景
三者账户数据均不落产融库，只回填 [[cust_account_info]]；产品维度路由存在默认值兜底（[[default_product_route_acflow]]）。与主表扩展字段 company_ext_data 承载的利率/建档来源信息无关，不可相互替代。

## 版本演进
暂无版本演进记录。