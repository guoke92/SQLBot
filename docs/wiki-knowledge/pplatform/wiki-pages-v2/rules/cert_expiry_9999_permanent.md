---
type: rule
title: 证件有效期 9999 视为长期
page_key: cert_expiry_9999_permanent
domain: 外部渠道与银行对接
status: draft
aliases:
  - 长期有效标识
  - timePermanent YES
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.initCustOfTianma
contract_version: "0.1"
belong: rules
---

证件有效期以 JSON 表达，到期日以 `9999` 开头时 status=YES 表示长期有效，否则 NO。

## 需求背景
营业执照与法人身份证共用同一表达方式，同时写入对应到期时间字段，便于运营侧直接索引；字段定义见 [[cust_company_info]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 证件有效期 9999 视为长期
content: 到期日以 9999 开头时 JSON status=YES，否则 NO；同时写 business_license_end_time / legal_certification_end_time
impact: 营业执照与法人证件有效期表达
field_targets:
  - cust_company_info.time_permanent
  - cust_company_info.legal_time_permanent
evidence: "code:CustAccessApplication.setCustCompany / initCustOfTianma"
```