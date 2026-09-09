---
type: caliber
title: AMS互通产品
page_key: caliber_ams_interworking_product
belong: calibers
domain: customer
status: published
aliases: []
oid: 1
sources: []
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义AMS互通产品的判定：`platform_product.id IN (ams.syslink.supplier, ams.syslink.project, ams.syslink.finance)`，由Nacos配置决定AMS供应商/项目/资金方产品。

## 需求背景

AMS互通产品用于判断租户或企业是否开通了AMS相关的产品能力，是查询企业用户列表的前置条件。

## 版本演进

口径来自代码证据，依赖Nacos配置。

```ground:caliber
name: AMS互通产品
predicate: "platform_product.id IN (ams.syslink.supplier, ams.syslink.project, ams.syslink.finance)"
scope: 由Nacos配置决定AMS供应商/项目/资金方产品
evidence: code
```