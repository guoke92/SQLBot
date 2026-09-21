---
type: concept
title: 管理员业务邮箱
page_key: admin_email_optional
belong: concepts
domain: cust
status: draft
aliases: [管理员邮箱非必填, 业务邮箱]
maps_to: cust_person_info.email
field_targets: [cust_person_info.email]
sources: ['code_path:CustImportCustInfoDTO.java:92', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [account_admin]
adjudication: boundary
---

# 管理员业务邮箱

document_claim:管理员邮箱非必填.md#23：邀请认证-客户录入时内管录入管理员邮箱非必填。
现网导入校验 require=false。列是人员 email，不是登录账号。问管理员仍过滤 user_type=accountAdmin。

## 页面链接

- [[tables/cust_person_info]]
- [[concepts/account_admin]]
