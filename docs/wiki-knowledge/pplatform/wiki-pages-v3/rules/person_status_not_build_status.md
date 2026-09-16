---
type: rule
title: 联系人激活不是建档过程
page_key: person_status_not_build_status
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
  - cust_person_info.status
  - cust_person_info.cust_build_status
---

status 是账号激活（未激活/已激活）；cust_build_status 是建档/认证过程，常从企业拷贝。未激活联系人不要用 BUILD_FAIL 去滤。

```ground:rule
name: 联系人激活不是建档过程
content: status 是账号激活（未激活/已激活）；cust_build_status 是建档/认证过程，常从企业拷贝。未激活联系人不要用 BUILD_FAIL 去滤。
field_targets: [cust_person_info.status, cust_person_info.cust_build_status]
evidence: "code_path:CustPersonStatusConstant.java:11"
```
