---
type: caliber
title: 交e保清分产品口径
page_key: calibers/bocom_clearing_product
domain: 外部渠道与银行对接
status: draft
aliases:
  - 交e保清分产品口径
  - bocom.clearing.allowedProductCodes
  - ACFLOW
  - RVSFACTOR_PC
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CpcnBankProviderImpl#listXylCustAccountBanks
contract_version: "0.1"
---

# 交e保清分产品口径

## 业务定位

该口径规定交e保（Cpcn）银行对接在查询/遍历客户的清分银行卡时，需要按配置的产品集合逐产品查询：`productCode IN ${bocom.clearing.allowedProductCodes:ACFLOW,RVSFACTOR_PC}`。该集合由 Nacos 配置项 `bocom.clearing.allowedProductCodes` 提供，缺省为 `ACFLOW,RVSFACTOR_PC`。

## 需求背景

同一客户可能同时开通多个产品的清分账户，因此银行侧账户查询必须以产品为维度展开；把产品集合做成可配置项，可以在不发布代码的前提下调整交e保清分覆盖的产品范围。该口径与 [[calibers/alipay_clearing_default_product]] 共同构成清分产品选择规则，`productCode` 的语义见 [[concepts/product_code]]。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 交e保清分产品口径
predicate: "productCode IN ${bocom.clearing.allowedProductCodes:ACFLOW,RVSFACTOR_PC}"
scope: CpcnBankProviderImpl.listXylCustAccountBanks 遍历该集合逐产品查清分银行卡
evidence: "code:CpcnBankProviderImpl（@NacosValue bocom.clearing.allowedProductCodes）"
```

## 关联页面

- 相关口径：[[calibers/alipay_clearing_default_product]]、[[calibers/bocom_account_existence]]
- 术语：[[concepts/product_code]]
- 载体表：[[tables/cust_company_info]]