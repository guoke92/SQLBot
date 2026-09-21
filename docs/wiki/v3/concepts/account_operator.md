---
type: concept
title: 经办人
page_key: account_operator
belong: concepts
domain: cust
status: draft
aliases: [经办人, operator, accountNormal]
maps_to: cust_person_info__user_type.accountNormal
field_targets: [cust_person_info__user_type.accountNormal, cust_person_info.user_type]
sources: ['code_path:UserTypeEnum.java:16', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [account_admin, skip_realname, archive_handby, login_account_term]
adjudication: boundary
---

# 经办人

Java 名 operator，入库 accountNormal。不要和管理员混用。经办人实名认证看 skip_auth_flag，不是 user_type。

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__user_type]]
- [[concepts/account_admin]]
- [[concepts/archive_handby]]
- [[concepts/login_account_term]]
- [[concepts/skip_realname]]
