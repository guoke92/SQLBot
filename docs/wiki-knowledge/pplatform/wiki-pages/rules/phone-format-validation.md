---
type: rule
title: 手机号格式校验
page_key: phone-format-validation
domain: 企业建档与准入
status: published
aliases: [手机号正则校验]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.phone]
scope:
  databases: [lowcode_pplatform]
---

# 手机号格式校验

本规则要求人员手机号必须匹配正则 `^1[3-9]\d{9}$`，用于企业建档时联系人手机号字段的格式约束。

## 需求背景

企业建档或人员新增时，手机号是重要的联系方式字段。格式校验在代码入口处执行，验证失败抛出参数错误并阻止建档。

## 版本演进

证据来自代码路径 `CustAccessApplication.isValidPhoneNumber`。

```ground:rule
name: 手机号格式校验
content: 手机号必须匹配正则 ^1[3-9]\d{9}$
impact: 验证失败抛出参数错误，阻止建档
field_targets:
  - cust_person_info.phone
evidence: "code_path:CustAccessApplication.isValidPhoneNumber"
```

相关表：[[联系人_客户人员]]

相关：[[cust_person_info]]
