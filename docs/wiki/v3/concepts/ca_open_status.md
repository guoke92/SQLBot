---
type: concept
title: CA证书/签章是否有效
page_key: ca_open_status
belong: concepts
domain: ca_fee
status: draft
aliases: [开通CA, CA状态]
maps_to: ca_fee_company.ca_status
field_targets: [ca_fee_company.ca_status, ca_certification_info.submit_status]
sources: ['code_path:CaFeeCertStatusEnum.java:15', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/ca证书收费.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_company, ca_certification_info]
also_confused_with: [ca_fee_paid]
adjudication: boundary
---

# CA证书/签章是否有效

缴费宽表 ca_status 来自签章中台快照（NORMAL 才有效）。
一证四步 SUCCESS 是采集提交成功，不是服务费已缴，也不是证书一定有效。

## 页面链接

- [[tables/ca_certification_info]]
- [[tables/ca_fee_company]]
- [[dicts/ca_certification_info__submit_status]]
- [[dicts/ca_fee_company__ca_status]]
- [[processes/ca_certification_info__submit_status]]
- [[concepts/ca_fee_paid]]
