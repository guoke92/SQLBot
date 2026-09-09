---
type: rule
title: AMS产品开通电子签章使用BEST_SIGN
page_key: ams-product-esign-best-sign
belong: rules
domain: AMS联系人第三方对接
status: published
aliases: [AMS电子签章签署机构]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

当产品为 AMS 时，companySignRegister 设置 signAgency=BEST_SIGN，并更新 bsRegisterStatus='Y'。

## 需求背景
AMS 产品电子签章签署机构与其他产品不同，需使用 BEST_SIGN。

## 版本演进
初始版本基于 CustAccessAsyncApplication.openCa / setSignRegister 提取。

```ground:rule
name: AMS产品开通电子签章使用BEST_SIGN
content: "当产品为AMS时，companySignRegister设置signAgency=BEST_SIGN，并更新bsRegisterStatus='Y'"
impact: "AMS产品电子签章签署机构与其他产品不同"
field_targets: ["CustCompanyInfoDO.bsRegisterStatus", "CustCompanyInfoDO.caRegisterStatus"]
evidence: "code_path:CustAccessAsyncApplication.openCa / setSignRegister"
```

[[cust_company_info_do]]