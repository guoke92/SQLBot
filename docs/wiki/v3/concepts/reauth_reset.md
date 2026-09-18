---
type: concept
title: 重新认证
page_key: reauth_reset
belong: concepts
domain: cust
status: draft
aliases: [终止认证]
maps_to: cust_company_info__cust_build_status.INIT
field_targets: [cust_company_info__cust_build_status.INIT, cust_company_info.cust_build_status]
sources: ['code_path:CustCompanyOperationApplication.java:165', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [build_success_not_effect, rebuild_archive_change]
adjudication: boundary
---

# 重新认证

document_claim:终止认证.md#15 写审核退回时可终止；现网接口名 reAuthentication，只允许待客户确认 CUST_CONFIRM_AWAIT 打回 INIT。
以代码为准。不是变更项「重新建档」UN0010。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[concepts/build_success_not_effect]]
- [[concepts/rebuild_archive_change]]
