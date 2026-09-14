---
type: caliber
title: 生效租户口径（activeList / enable 与 status 双判定）
page_key: tenant_active_list
domain: 平台内部服务对接
status: draft
aliases:
  - 生效租户
  - activeList
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.enable / status]
contract_version: "0.1"
belong: calibers
---

租户配置的生效判定需同时满足有效标志与生效标志，查询生效租户时以 activeList 形式取用。

## 需求背景

租户配置项（[[tables/tenant_setting_config]]）是平台内部服务对接的前置条件，未生效租户不应参与 token 换取与互通系统拉取。

## 版本演进

v0：首次成页。

```ground:caliber
name: 生效租户口径
field: tenant_setting_config.enable / status
values:
  - "'Y'"
criterion: "查询生效租户 activeList、'Y' 判定"
evidence: code
```