---
type: concept
title: 企业管理员
page_key: account_admin
belong: concepts
domain: cust
status: draft
aliases: [管理员, admin, accountAdmin]
maps_to: cust_person_info__user_type.accountAdmin
field_targets: [cust_person_info__user_type.accountAdmin, cust_person_info.user_type]
sources: ['code_path:UserTypeEnum.java:15', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [account_operator, admin_email_optional]
adjudication: boundary
---

# 企业管理员

UserTypeEnum 的 Java 名是 admin，入库 dictKey 是 accountAdmin，中文是管理员。
问管理员过滤 user_type=accountAdmin，不要用枚举名 admin。

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__user_type]]
- [[concepts/account_operator]]
- [[concepts/admin_email_optional]]
