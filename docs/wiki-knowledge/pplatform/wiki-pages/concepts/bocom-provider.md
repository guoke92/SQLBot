---
type: concept
title: 交e保
page_key: bocom-provider
domain: 企业银行账户与第三方银行
status: published
aliases: ["Bocom", "清分", "清分会员登记簿"]
oid: 1
sources: ["code"]
contract_version: "0.1"
maps_to: "BocomProvider / BocomFacade 接口族"
field_targets: []
adjudication: boundary
also_confused_with: ["CFCA中金支付", "CpcnBankProviderImpl"]
boundary: "交e保由BocomProvider/BocomFacade承载；CFCA中金支付由BankProvider/CpcnBankProviderImpl承载"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

术语“交e保”指第三方银行/清分服务，由 `BocomProvider / BocomFacade` 接口族承载。该术语桥将其与 CFCA 中金支付区分。

## 需求背景

在第三方银行接入中，交e保与中金支付使用不同的接口提供方。业务上需明确两者承载的类与边界，避免路由错误。

## 版本演进

本概念契约 v0 基于代码证据建立，划分服务提供方边界。

相关路由规则参见 [[third-party-bank-product-routing]]。