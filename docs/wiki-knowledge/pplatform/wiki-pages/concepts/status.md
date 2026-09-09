---
type: concept
title: status（生效状态）
page_key: status
belong: concepts
domain: tenant-config-operation-email
status: published
aliases: [生效状态]
oid: 1
sources: [db, db_dist, term_bridge]
contract_version: "0.1"
maps_to: "tenant_setting_config.status"
field_targets: ["tenant_setting_config.status"]
adjudication: boundary
also_confused_with: ["enable"]
boundary: "status 表示租户是否已生效（业务生效），enable 表示逻辑删除标记"
scope:
  databases: [lowcode_pplatform]
---

`status` 字段在 `tenant_setting_config` 中表示租户是否已生效，取值为 Y（已生效）或 N（未生效/待生效）。与 `enable` 的逻辑删除标记不同，它关注业务生效状态。

## 需求背景

租户需要经过生效条件校验后才能从待生效进入已生效，`status` 用于表达这一业务状态，便于业务查询与操作控制。

## 版本演进

- 初版（v0.1）：术语桥判定为 boundary，区分 `status` 与 `enable`。

[[tenant_setting_config]] [[tenant-status]]