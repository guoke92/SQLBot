---
type: concept
title: 集团根标识（root_flag）
page_key: root-flag
domain: 企业集团关系
status: draft
aliases: [root_flag, rootFlag]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java
contract_version: "0.1"
maps_to: "cust_group_rel.root_flag = 'Y'（集团本身）/ 'N'（成员单位）"
field_targets:
  - cust_group_rel.root_flag
  - cust_group_rel.root_group_id
  - cust_group_rel.root_cust_id
adjudication: boundary
also_confused_with:
  - root_group_id（根关系记录主键）
  - root_cust_id（根企业id）
boundary: root_flag=Y 的节点不允许再作为子级关联、也不允许签署成员单位协议；root_group_id/root_cust_id 是树定位字段，与布尔标识无关。
sources: ["enrich:wiki-admin"]
belong: concepts
---

集团根标识用于区分一行关系记录代表的是集团本身（Y）还是成员单位（N），是权限与树结构的判定基础，口径见 [[calibers/group-root-node]]，表见 [[tables/cust_group_rel]]。

## 需求背景

根节点与成员单位在操作权限上互斥：根节点不能再作为其他集团的子级，也不能签署成员单位协议，因此必须有一个明确的布尔标识承载该判定；树定位则另由 root_group_id / root_cust_id 承担，见 [[processes/cust-group-rel-status-state]]。

## 版本演进

v0 契约按现状固化，标识与树定位字段职责分离。

## 判定边界

root_flag=Y 的节点不允许再作为子级关联、也不允许签署成员单位协议；root_group_id/root_cust_id 是树定位字段，与布尔标识无关。

相关：[[cust_group_rel]]
