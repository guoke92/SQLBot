---
type: rule
title: 变更项包含性判定
page_key: change_item_contains
domain: 企业变更与运营变更
status: draft
aliases: [checkChangeItems, alter_type_id 解析]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: rules
---

规则内容：`alter_type_id` 按逗号拆分后 `in cust_change_cfg.id` 批量查询，再判断命中记录的 `item_code` 是否落在目标编码集合中，作为跳转分支判定依据（[[admin_mobile_redirect]]）。

## 需求背景

变更记录上存的是配置主键列表而非编码列表，任何按编码的判定都必须经配置表翻译一次，该规则固化翻译链路，避免直接比较 `alter_type_id` 与 `item_code`。

## 版本演进

v0.1：首次固化。

```ground:rule
name: 变更项包含性判定
content: "alter_type_id 按逗号拆分后 in cust_change_cfg.id 批量查询，再判断命中记录的 item_code 是否落在目标编码集合中"
impact: 跳转分支判定依据
field_targets:
  - cust_change_record.alter_type_id
  - cust_change_cfg.id
  - cust_change_cfg.item_code
evidence: "code_path:CustChangeApplication.java#checkChangeItems"
```

相关页面：[[change_item_code]]、[[cust_change_cfg]]、[[cust_change_record]]、[[admin_mobile_change_items]]。