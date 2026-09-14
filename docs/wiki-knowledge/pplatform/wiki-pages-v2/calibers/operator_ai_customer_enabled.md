---
type: caliber
title: 开启智能客服口径（operator_ai_customer='1'）
page_key: operator_ai_customer_enabled
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [开启智能客服, operator_ai_customer='1']
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config.operator_ai_customer '1'=15 / '0'=108"
  - "code:TenantDomainService.updateOperationConfigById 直写"
contract_version: "0.1"
belong: calibers
---

「开启智能客服」判定为 `operator_ai_customer='1'`。该字段是 0/1 字符口径而非 Y/N，是本表内最容易与布尔口径混淆的字段之一，引用时不可套用 enable/status 的 Y/N 判断。

表结构见 [[tenant_setting_config]]。

## 需求背景
智能客服入口按租户灰度开通，需要与智能客服按钮颜色（ai_resource_color）一起下发。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；0/1 口径已由 DB 分布证实，不再与 Y/N 混用。

```ground:caliber
name: 开启智能客服
predicate: "tenant_setting_config.operator_ai_customer = '1'"
scope: "智能客服入口开关（注意非 Y/N 口径）"
evidence: "db:'1'=15 / '0'=108；code:TenantDomainService.updateOperationConfigById 直写"
```