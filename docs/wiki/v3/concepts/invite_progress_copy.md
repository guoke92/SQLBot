---
type: concept
title: 邀请进度抄建档状态
page_key: invite_progress_copy
belong: concepts
domain: cust
status: draft
aliases: [邀请进度, progress, 邀请供应商]
maps_to: cust_invite_info.progress
field_targets: [cust_invite_info.progress, cust_company_info.cust_build_status]
sources: ['code_path:CustSyncEventProcessor.java:1128', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_invite_info, cust_company_info]
also_confused_with: [invite_customer_entry]
adjudication: boundary
---

# 邀请进度抄建档状态

progress 码集与 cust_build_status 相同，但是邀请表自己的列。
document_claim:邀请供应商功能.md#15：核心企业邀请供应商落在 cust_invite_info。
回写按被邀请企业 name+db_tenant_code 匹配，不是 invite_cust_id JOIN。

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_invite_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_invite_info__progress]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_invite_info__progress]]
- [[concepts/invite_customer_entry]]
