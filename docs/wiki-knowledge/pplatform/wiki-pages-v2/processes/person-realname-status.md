---
type: process
title: 实名认证状态
page_key: person-realname-status
domain: 客户联系人管理
status: draft
aliases:
  - 手机实名状态流转
  - phone_realname_status 状态机
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code_path:CustPersonApplication.java:insertOrUpdatePerson"
  - "code_path:CustPersonApplication.java:updateVerifyNameStatus"
contract_version: "0.1"
belong: processes
---

实名认证状态落在 [[tables/cust_person_info]] 的 `phone_realname_status` 字段，描述经办人手机实名认证的进展。自动认证与人工认证是两条通过路径，均以 `TO_BE_VERIFIED` 为起点。

## 需求背景

经办人提交资料后先处于待认证；系统自动核验通过则落自动认证通过，自动核验不通过的场景由运营人工复核，人工通过后落人工认证通过。前端据此决定是否弹出实名认证引导，口径见 [[calibers/realname-pending]]、[[calibers/realname-passed]]；特定角色允许豁免认证，见 [[rules/skip-realname-limit]] 与 [[calibers/realname-skip]]。

```ground:process
process: 实名认证状态
field: cust_person_info.phone_realname_status
states:
  - value: TO_BE_VERIFIED
    label: 待认证
    source: db_dist
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: db_dist
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: db_dist
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动认证失败
    source: db_dist
transitions:
  - from: TO_BE_VERIFIED
    event: 自动实名认证通过
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: "code_path:CustPersonApplication.java:insertOrUpdatePerson"
  - from: TO_BE_VERIFIED
    event: 人工实名认证通过
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: "code_path:CustPersonApplication.java:updateVerifyNameStatus"
```

## 版本演进

- v0：首次登记。`AUTOMATIC_AUTHENTICATION_FAILED` 的后续流转（转人工/重试）在现有证据中未见明确迁移边，暂不登记。

相关：[[tables/cust_person_info]]、[[calibers/realname-pending]]、[[calibers/realname-passed]]、[[rules/skip-realname-limit]]。