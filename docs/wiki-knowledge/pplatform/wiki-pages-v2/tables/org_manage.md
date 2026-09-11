---
type: table
title: 机构管理表 org_manage
page_key: table.org_manage
domain: 数据权限与组织
status: draft
aliases: [org_manage, 机构表, 机构管理]
oid: 1
scope:
  databases: [base]
sources: [db, code]
contract_version: "0.1"
---


机构域主数据表，通过 parent_code 自引用构成机构树。organization_id 与 [[tables/operation_user]].organization_id 属同一机构域主键，二者构成 [[concepts/org_identity_bridge]]；org_type 与代码侧 OrgTypeEnum（ORG 根机构 / SUB 子机构）对应；client_type 用于区分来源端，代码 OrgFacade 中以 clientType=='AGW' 判断是否跳过租户过滤，见 [[rules/org_agw_skip_tenant_filter]]。

org_name 与 name 的区别在于前者面向展示，建档与查询口径应以 org_name 为准。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自 db 字段语义与代码侧（OrgTypeEnum、SysOrgDO.parentId/selectByCode、OrgFacade）证据。

## 版本演进

v0：依据 db + code 证据建档。

```ground:table
table: org_manage
database: lowcode_pplatform
desc: 机构管理
inactive: true
fields:
  - name: id
    desc: 机构管理主键
  - name: org_name
    desc: 机构名称（面向展示的名称字段，区别于 name）
  - name: org_no
    desc: 机构号
  - name: org_level
    desc: 机构层级（int，机构树的深度）
  - name: org_type
    desc: 机构类型（varchar32，与代码侧 OrgTypeEnum：ORG 根机构 / SUB 子机构 对应）
  - name: parent_code
    desc: 父机构编号（自引用，构成机构树；对应代码 SysOrgDO.parentId/selectByCode 链路）
  - name: organization_id
    desc: 机构编号（与 operation_user.organization_id 同域的机构主键）
  - name: status
    desc: 状态
  - name: client_type
    desc: 端类型（区分 AGW/客户端等来源；代码 OrgFacade 中以 clientType=='AGW' 判断是否跳过租户过滤）
  - name: enable
    desc: enable（默认 Y）
  - name: db_tenant_code
    desc: 数据租户标识
  - name: app_tenant_code
    desc: 逻辑租户标识
```