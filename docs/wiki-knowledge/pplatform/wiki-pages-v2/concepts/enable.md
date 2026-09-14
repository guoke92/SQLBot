---
type: concept
title: 启用
page_key: enable
domain: 准入接入与接入密钥
status: draft
aliases:
  - enable
  - Y/N
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret.enable
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_access_secret.enable
also_confused_with:
  - tenant_setting_config.enable
  - cust_company_info.enable
adjudication: boundary
boundary: 不同表的enable是各自独立过滤条件，不能跨表复用。
belong: concepts
field_targets: [cust_access_secret.enable]
sources: ["enrich:wiki-admin"]
---

# 启用

## 业务定位

`enable` 是软开关字段，取值 `Y` / `N`。在接入链路上，只有 `cust_access_secret.enable = 'Y'` 的渠道才被认为有效（[[calibers/valid_access_channel|有效接入渠道]]），`N` 即为 [[calibers/disabled_access_channel|禁用接入渠道]]。

## 边界与混淆

同名字段在不同表上语义独立：`tenant_setting_config.enable`、`cust_company_info.enable` 各自是所在表的过滤条件，不能跨表套用；接入校验只认可 `cust_access_secret.enable`。

## 需求背景

渠道停用需要可回退且不删除配置，因此采用 Y/N 软开关，配合校验逻辑在入口拦截。

## 版本演进

DB 实测 Y=19、N=2，取值集合稳定为 Y/N。

相关：[[cust_access_secret]]
