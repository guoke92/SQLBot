---
type: concept
title: 冻结解冻留痕
page_key: freeze_audit
belong: concepts
domain: cust
status: draft
aliases: [冻结原因, 解冻记录, 冻结依据]
maps_to: cust_company_lifecycle_info.type
field_targets: [cust_company_lifecycle_info.company_id, cust_company_lifecycle_info.type,
  cust_company_lifecycle_info.reason, cust_company_lifecycle_info.attach]
sources: ['code_path:CustCompanyInfoApplication.java:7064', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_lifecycle_info]
also_confused_with: [account_admin]
adjudication: boundary
---

# 冻结解冻留痕

V1.19 要求冻结/解冻必填原因和依据文件。现网落在 cust_company_lifecycle_info：type=FRZ/UNFRZ，company_id 企业主键。
预生成 enable=N，确认后 enable=Y。不要把企业冻结理解成改管理员 enable。
document_claim:冻结解冻留痕.md#15

## 页面链接

- [[tables/cust_company_lifecycle_info]]
- [[dicts/cust_company_lifecycle_info__type]]
- [[concepts/account_admin]]
