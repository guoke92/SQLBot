---
type: rule
title: 分项认证不是综合实名
page_key: face_not_real_name_result
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
  - cust_person_info.face_status
  - cust_person_info.real_name_result
---

face_status / phone_realname_status 是分项；综合结论是 real_name_result。任一项通过即为综合成功。

```ground:rule
name: 分项认证不是综合实名
content: face_status / phone_realname_status 是分项；综合结论是 real_name_result。任一项通过即为综合成功。
field_targets: [cust_person_info.face_status, cust_person_info.real_name_result]
evidence: "code_path:RealNameResultEnum.java:66"
```
