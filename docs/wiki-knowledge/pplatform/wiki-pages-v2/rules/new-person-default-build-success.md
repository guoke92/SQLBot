---
type: rule
title: 经办人新增来源默认认证通过
page_key: new-person-default-build-success
domain: 客户联系人管理
status: draft
aliases:
  - 非AMS来源默认建档成功
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.insertOrUpdatePerson"
contract_version: "0.1"
belong: rules
---

非 AMS 来源新增经办人时，默认设置建档状态为 `BUILD_SUCCESS`（即默认认证通过）。

## 需求背景

`source` 标识联系人来源（`AMS`=运营中台，`longteng`=龙腾），来自非运营中台渠道的经办人视为已完成线下建档与审核，因此落库时直接置为建档成功；AMS 来源仍走 [[processes/person-build-status]] 的完整审核流程。该默认值会直接影响经办人的后续实名认证路径，见 [[processes/person-realname-status]]。

```ground:rule
rule: 经办人新增来源默认认证通过
content: 非AMS来源新增经办人时，默认设置建档状态为BUILD_SUCCESS（即默认认证通过）
impact: 影响经办人的建档状态和后续实名认证流程
field_targets:
  - cust_person_info.cust_build_status
  - cust_person_info.source
evidence: "code:CustPersonApplication.insertOrUpdatePerson"
```

## 版本演进

- v0：首次登记。

相关：[[processes/person-build-status]]、[[calibers/person-operator]]、[[tables/cust_person_info]]。