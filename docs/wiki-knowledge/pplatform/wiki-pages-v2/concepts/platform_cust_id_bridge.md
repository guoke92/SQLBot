---
type: concept
title: 运营中台企业 id 术语桥（custEnterpriseId / platform_cust_id）
page_key: platform_cust_id_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - custEnterpriseId
  - platform_cust_id
  - 运营中台企业id
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_role_info.platform_cust_id]
  - semantic:field_semantics[cust_change_record.cust_id / status / oper_cust_info / oper_channel / create_time]
contract_version: "0.1"
maps_to:
  - term: custEnterpriseId
    target: cust_role_info.platform_cust_id
    evidence: code
  - term: oper_cust_info.custEnterpriseId
    target: cust_role_info.platform_cust_id
    evidence: code
field_targets:
  - cust_role_info.platform_cust_id
  - cust_change_record.oper_cust_info
belong: concepts
---

运营中台侧的企业 id（custEnterpriseId）在平台库内落在 cust_role_info.platform_cust_id，用于换取 token / 授权；客户变更记录把同一 id 存进 oper_cust_info JSON。

## 需求背景

两个来源并非随时可互换：企业处于变更流程时，token 所需的运营中台 id 取自变更记录（见 [[rules/change_status_token_source]]）；常态下取角色表字段。

## 版本演进

v0：首次成页。