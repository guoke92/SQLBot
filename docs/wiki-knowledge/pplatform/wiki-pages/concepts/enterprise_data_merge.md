---
type: concept
title: 企业数据合并
page_key: enterprise_data_merge
belong: concepts
domain: 租户迁移
status: published
aliases: [存量企业合并]
oid: 17
maps_to: "cust_company_info.certification_no"
field_targets: [cust_company_info.certification_no]
adjudication: boundary
also_confused_with: [social_unified_code]
boundary: "代码以统一社会信用代码(certification_no)+db_tenant_code 作为已有企业识别，进行角色/联系人补全而非重复建档"
sources: [code, db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：AMS 与讯易链存量企业数据合并，保留一条。

## 需求背景
需求侧确认：AMS 与讯易链存量企业需数据合并，保留一条。代码证实：存在相同 certNo 企业时补角色/联系人，不新建建档。

## 版本演进
v0.1 基于代码与术语桥边界定义。

关联：[[ams_enterprise_merge]] [[cust_company_info]]