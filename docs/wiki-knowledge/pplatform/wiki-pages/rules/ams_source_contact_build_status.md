---
type: rule
title: AMS来源联系人建设状态不默认通过
page_key: rules/ams-source-contact-build-status
domain: AMS联系人第三方对接
status: published
aliases: [AMS联系人建档状态]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

insertOrUpdatePerson 中，非 AMS 来源新增经办人默认 custBuildStatus=BUILD_SUCCESS；AMS 来源不设置默认值，建设状态由后续认证流程决定。

## 需求背景
AMS 来源联系人可能需要额外认证流程，因此不能默认通过。

## 版本演进
初始版本基于 CustPersonApplication.insertOrUpdatePerson 提取。

```ground:rule
name: AMS来源联系人建设状态不默认通过
content: "insertOrUpdatePerson中，非AMS来源新增经办人默认custBuildStatus=BUILD_SUCCESS；AMS来源不设置默认值"
impact: "AMS来源联系人可能需要额外认证流程"
field_targets: ["CustPersonInfoDO.custBuildStatus"]
evidence: "code_path:CustPersonApplication.insertOrUpdatePerson"
```

[[AMS联系人]] [[cust_person_info_do]]