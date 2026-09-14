---
type: concept
title: 客户变更 / 企业变更
page_key: customer_change
domain: 企业变更与运营变更
status: draft
aliases: [企业变更, 企业信息变更, 客户变更]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - db:cust_oper_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: null
field_targets:
  - cust_change_record.cust_id
  - cust_oper_change_record.person_id
adjudication: boundary
also_confused_with:
  - cust_oper_change_record
belong: concepts
---

「客户变更 / 企业变更」在本域内特指企业客户信息与资质的变更，落 [[cust_change_record]]，走审核状态机 [[cust_change_record_status]]。

边界：`cust_change_record` 是企业客户信息/资质变更；[[cust_oper_change_record]] 是企业联系人（运营人员）归属变更记录。两者表、触发源、状态字段均不同，不能合并统计。

本术语指向的是业务实体而非单个字段，因此不在 `maps_to` 上落字段锚点，改由 `field_targets` 记录两侧的判别字段。

## 需求背景

两类「变更」在中文口语中高度重合（都叫「变更」），但一侧影响企业资质、一侧影响服务归属，混淆会导致统计与权限判断出错，故单列术语桥。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[cust_oper_change_record]]、[[operator]]、[[alter_mode]]。

---REVIEW: concept | 客户变更 / 企业变更---
该术语的所指是实体级（表），按 concept 页约定 `maps_to` 必须是「表.字段」或 dictKey.VALUE，故本页暂置 `maps_to: null`，仅以 `field_targets` 记录判别字段。需要维护者决策：是接受实体级 `maps_to: cust_change_record`，还是在本域新增一层聚合概念页。
---END REVIEW---