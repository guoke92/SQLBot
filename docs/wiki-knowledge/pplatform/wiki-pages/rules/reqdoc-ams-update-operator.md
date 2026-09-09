---
type: rule
title: AMS通知产融更新经办人信息
page_key: reqdoc-ams-update-operator
belong: rules
domain: AMS联系人第三方对接
status: published
aliases: [AMS更新经办人通知]
oid: 1
sources:
  - code
  - reqdoc
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

AMS 通知产融更新经办人信息，由 PlatFormAmsProviderImpl.updateOperator 承载。

## 需求背景
AMS 侧发起更新经办人请求，产融平台接收并处理。需求文档与代码实现一致。

## 版本演进
初始版本为需求文档主张，已由代码证据确认。

```ground:rule
name: "AMS通知产融更新经办人信息"
content: "AMS通知产融更新经办人信息"
impact: ""
field_targets: []
evidence: "code_path:PlatFormAmsProviderImpl.updateOperator + reqdoc:AMS通知产融更新经办人信息"
code_status: confirmed
action: anchor
```

[[operator]] [[cust_person_info_do]]