---
type: rule
title: 新增联系人响应码约定
page_key: rules/add-enterprise-contact-response-code
domain: AMS联系人第三方对接
status: published
aliases: [响应码约定]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

新增企业联系人接口（addEnterpriseContact）成功和异常情况下的响应码约定，供 AMS 侧判断处理结果。

## 需求背景
AMS 通知产融新增企业联系人时，需要根据响应码判断处理结果。成功返回 code=200,resultCode=02；异常返回 code=500,resultCode=04。

## 版本演进
初始版本基于 PlatFormAmsProviderImpl.addEnterpriseContact 提取。

```ground:rule
name: 新增联系人响应码约定
content: "addEnterpriseContact成功返回code=200,resultCode=02；异常返回code=500,resultCode=04"
impact: "AMS侧需根据响应码判断处理结果"
field_targets: ["AddEnterpriseContactResponse.code", "AddEnterpriseContactResponse.resultCode"]
evidence: "code_path:PlatFormAmsProviderImpl.addEnterpriseContact"
```

[[enterprise_contact_concurrency_lock]]