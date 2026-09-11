---
type: caliber
title: 有效标志口径（enable='Y'）
page_key: caliber.enable_valid_flag
domain: 平台内部服务对接
status: draft
aliases:
  - 有效标志
  - enable 口径
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.enable]
  - semantic:field_semantics[cust_person_info.enable]
  - semantic:field_semantics[cust_project_rel.enable]
  - semantic:field_semantics[tenant_setting_config.enable / status]
contract_version: "0.1"
---

「有效」在多数业务表中的表达方式为字符标志位，取值 'Y'/'N'。

## 需求背景

企业查询一律附加 .eq(enable, 'Y')（见 [[rules/company_query_enable_y]]）；联系人侧的 enable 会因经办人权限被逻辑改写，因此不能等同于企业侧口径，二者同时参与有效数据判定时需分别处理（见 [[rules/operator_permission_disable]]）。租户侧的生效判定还要叠加 status（见 [[calibers/tenant_active_list]]）。

## 版本演进

v0：首次成页。

```ground:caliber
name: 有效标志口径
field: enable
values:
  - "'Y'"
  - "'N'"
criterion: "查询有效数据一律 .eq(enable, 'Y')"
applies_to:
  - cust_company_info.enable
  - cust_person_info.enable
  - cust_project_rel.enable
evidence: code
```