---
type: concept
title: CA 已开通
page_key: ca_registered
domain: CA证书认证
status: draft
aliases: [已注册CA, 电子签章已开通]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:OpenStatus.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
maps_to: cust_company_info.ca_register_status
field_targets: [cust_company_info.ca_register_status]
adjudication: boundary
boundary: 企业是否已开通签章落 ca_register_status；收费台账证书观感落 ca_fee_company.ca_status；上送是否成功落 submit_status
also_confused_with: [ca_fee_company.ca_status, ca_certification_info.submit_status]
---

「CA 已开通」落 [[cust_company_info]] 的 `ca_register_status='Y'`（口径 [[ca_registered_company]]）。

上送成功（[[ca_submit_success]]）不等于企业已开通。收费场景筛「证书正常」用 [[ca_status]]=`NORMAL`，不要用本列。
