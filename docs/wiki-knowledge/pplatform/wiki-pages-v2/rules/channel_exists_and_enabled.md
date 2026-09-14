---
type: rule
title: 渠道存在且启用校验
page_key: channel_exists_and_enabled
domain: 准入接入
status: draft
aliases: [渠道校验, 渠道不存在]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
belong: rules
---

接入请求进入后，系统按请求中的渠道标识检索 [[tables/cust_access_secret]]：记录必须存在，且 `enable = 'Y'`；任一条件不满足即抛出“渠道不存在”异常，请求被拒绝。

这条规则是准入链路的入口闸门，阻止非法渠道接入。它依赖术语 [[concepts/channel]] 与 [[concepts/enable]]，以及口径 [[calibers/channel_lookup]]、[[calibers/access_secret_enable_valid]]；通过后进入 [[rules/channel_tenant_exists]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValue`。

```ground:rule
name: 渠道存在且启用校验
content: 根据请求中的channel查询cust_access_secret，必须存在且enable='Y'，否则抛出'渠道不存在'异常
impact: 阻止非法渠道接入
field_targets:
  - cust_access_secret.channel
  - cust_access_secret.enable
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```