---
type: rule
title: 联系人类型不是企业角色
page_key: user_type_not_company_type
domain: 经办人/联系人/管理员管理
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - cust_person_info.user_type
  - cust_person_info.company_type
---

user_type 答管理员/经办人/游客；company_type 答供应商/核心企业等。混用会把「核心企业」当成管理员。

```ground:rule
name: 联系人类型不是企业角色
content: user_type 答管理员/经办人/游客；company_type 答供应商/核心企业等。混用会把「核心企业」当成管理员。
field_targets: [cust_person_info.user_type, cust_person_info.company_type]
evidence: "code_path:UserTypeEnum.java:15"
```
