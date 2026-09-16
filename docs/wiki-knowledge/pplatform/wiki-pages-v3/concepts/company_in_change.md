---
type: concept
title: 变更中
page_key: company_in_change
domain: 企业变更与运营变更
status: draft
aliases: [企业变更中]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustStatusEnum.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
maps_to: cust_company_info.cust_status
field_targets: [cust_company_info.cust_status]
adjudication: boundary
boundary: 企业是否变更中落 cust_status=CHANGE；变更单是否在审落 cust_change_record.status
also_confused_with: [cust_change_record.status]
---

「变更中企业」落 [[cust_company_info]] 的 `cust_status='CHANGE'`（口径 [[in_change_company]]）。变更单审核中用 [[pending_change]]。建档过程态是 [[cust_build_status]]，准入审核是 [[check_status]]。
