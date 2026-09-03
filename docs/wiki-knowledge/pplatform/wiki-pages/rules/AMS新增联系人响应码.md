---
type: rule
title: AMS新增联系人响应码
page_key: rule_ams_add_contact_response_code
domain: customer
status: published
aliases: []
oid: 1
sources: []
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则定义AMS新增联系人接口的响应码约定，用于第三方识别处理结果。

## 需求背景

对于AMS第三方对接，响应码的标准化有助于对方系统处理。成功时 `code=200` 且 `resultCode=02`；异常时 `code=500` 且 `resultCode=04`。

## 版本演进

规则来自代码路径 `PlatFormAmsProviderImpl.addEnterpriseContact`，无文档声明冲突。

```ground:rule
name: AMS新增联系人响应码
content: "成功code=200且resultCode=02；异常code=500且resultCode=04"
impact: 第三方根据resultCode识别处理结果
field_targets: []
evidence: "code_path:PlatFormAmsProviderImpl.addEnterpriseContact"
```