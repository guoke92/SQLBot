---
type: concept
title: 假贴牌
page_key: fake_branding
domain: 租户迁移
status: published
aliases: [二级贴牌]
oid: 16
maps_to: "cust_company_info.tenant_flg_en"
field_targets: [cust_company_info.tenant_flg_en]
adjudication: boundary
also_confused_with: [app_tenant_code, band_name]
boundary: "需求侧假贴牌/二级贴牌未在给定代码/DB中形成独立状态字段；tenant_flg_en 是项目标识入参，不可等同于假贴牌"
sources: [db, code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：需求侧概念，表示二级贴牌。

## 需求背景
(document_claim，未证实) 以下声明未证实：
- 假贴牌在租户配置表单内不可见，仅后台存在
- 假贴牌作为二级贴牌挂在自营贴牌下
- 内管端可正常创建二级贴牌下的项目

## 版本演进
v0.1 该概念在给定代码/DB中无独立状态字段；tenant_flg_en 为项目标识入参，不可等同。

关联：[[cust_company_info]]