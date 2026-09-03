---
type: rule
title: AMS通知产融新增企业联系人
page_key: rules/reqdoc-ams-add-enterprise-contact
domain: AMS联系人第三方对接
status: published
aliases: [AMS新增企业联系人通知]
oid: 1
sources:
  - code
  - reqdoc
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

AMS 通知产融新增企业联系人，由 PlatFormAmsProviderImpl.addEnterpriseContact 承载。

## 需求背景
AMS 侧发起新增企业联系人请求，产融平台接收并处理。需求文档与代码实现一致。

## 版本演进
初始版本为需求文档主张，已由代码证据确认。

```ground:rule
name: "AMS通知产融新增企业联系人"
content: "AMS通知产融新增企业联系人"
impact: ""
field_targets: []
evidence: "code_path:PlatFormAmsProviderImpl.addEnterpriseContact + reqdoc:AMS通知产融新增企业联系人"
code_status: confirmed
action: anchor
```

[[enterprise_contact_concurrency_lock]] [[add_enterprise_contact_response_code]]