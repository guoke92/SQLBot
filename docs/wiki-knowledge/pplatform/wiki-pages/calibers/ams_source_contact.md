---
type: caliber
title: AMS来源联系人
page_key: calibers/ams-source-contact
domain: AMS联系人第三方对接
status: published
aliases: [AMS来源人员, AMS联系人来源]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

AMS 来源联系人是指 CustPersonInfoDO.source 等于 'AMS' 的联系人。该口径约束新增联系人时的建设状态处理。

## 需求背景
当新增联系人来源为 AMS 时，不应默认设置 custBuildStatus=BUILD_SUCCESS，后续由认证流程决定；非 AMS 来源新增经办人默认置为 BUILD_SUCCESS。

## 版本演进
初始版本基于 insertOrUpdatePerson 代码提取。

```ground:caliber
name: AMS来源联系人
predicate: "CustPersonInfoDO.source = 'AMS'"
scope: "新增联系人时，AMS来源不默认设置custBuildStatus=BUILD_SUCCESS，由后续认证流程决定"
evidence: "code_path:CustPersonApplication.insertOrUpdatePerson"
```

[[cust_person_info_do]] [[ams_source_contact_build_status]]