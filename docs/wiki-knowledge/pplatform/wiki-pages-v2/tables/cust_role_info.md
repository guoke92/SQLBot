---
type: table
title: cust_role_info（企业角色授权表）
page_key: table.cust_role_info
domain: 平台内部服务对接
status: draft
aliases:
  - cust_role_info
  - 企业角色表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_role_info]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


企业角色维度表，一个「企业 code + 角色」一行，用于承接运营中台企业 id（platform_cust_id）并参与换取 token / 授权。

## 需求背景

企业角色在 [[tables/cust_company_info]] 中以 JSON 数组存放，在关系表中拆成单值记录（见 [[concepts/company_role_bridge]]）。角色状态不独立演进，而是随企业状态联动更新（见 [[rules/role_status_follow_company]]）。

## 版本演进

v0：首次成页。

```ground:table
table: cust_role_info
fields:
  - name: role_type
    desc: 企业角色类型（与 cust_company_info.cust_company_type 同域；initRootOrg 按此字段逐角色初始化根组织）
  - name: platform_cust_id
    desc: 运营中台企业ID（未同步时置空，作为待补推标记）
  - name: ref_cust_company_info
    desc: 关联企业业务编码
  - name: status
    desc: 角色状态（随企业状态联动更新）
  - name: enable
    desc: 角色有效标识；按角色同步时取有效角色（enable='Y'）
```
## 关联表

- [[cust_auth_application]]：cust_role_info.ref_cust_auth_application → cust_auth_application.code（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_change_record]]：cust_role_info.ref_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_role_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustRoleInfoDO.java，suggested）
