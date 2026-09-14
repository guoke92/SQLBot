---
type: caliber
title: 平台运营方取值口径（PLATFORM / TENANT）
page_key: platform_operator_value
domain: 平台内部服务对接
status: draft
aliases:
  - 平台运营方
  - platform_operator
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.platform_operator]
contract_version: "0.1"
belong: calibers
---

tenant_setting_config.platform_operator 以 JSON 数组存放平台运营方，取值 PLATFORM（联易融）或 TENANT（租户自身）。

## 需求背景

该字段决定运营主体归属，影响对接链路上由谁提供运营能力。它是数组结构而非单值，判定时需按集合语义处理。

## 版本演进

v0：首次成页。

```ground:caliber
name: 平台运营方取值口径
field: tenant_setting_config.platform_operator
values:
  - PLATFORM
  - TENANT
criterion: "JSON 数组，取值 PLATFORM（联易融）/TENANT（租户自身）"
evidence: code
```