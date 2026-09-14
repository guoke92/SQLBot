---
type: rule
title: 自主/非自主建档校验分档
page_key: independent_archive_validation
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档校验分档
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateMedia
  - code:CustAccessApplication.validateBank
contract_version: "0.1"
belong: rules
---

建档校验按是否自主（isIndependent）分两档：自主建档对联系人/法人证件与手机号做非空后校验，非自主建档强制校验并须提交完整影像与供应商银行三要素。

## 需求背景
非自主建档由渠道代客提交，资料完整性完全依赖渠道，因此准入与影像要求更严；影像落地依赖 [[sftp_channel_enable]]，银行三要素落点见 [[cust_account_info]]，概念背景见 [[company_archive]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 自主/非自主建档校验分档
content: 自主建档(isIndependent=true)对联系人/法人证件与手机号做非空后校验；非自主建档强制校验且必须提交授权书+法人正反面+经办人正反面+营业执照影像及供应商银行三要素
impact: 建档准入与影像完整性
field_targets:
  - cust_company_info.certification_no
  - cust_account_info.bank_no
evidence: "code:CustAccessApplication.validateSetValue / validateMedia / validateBank"
```