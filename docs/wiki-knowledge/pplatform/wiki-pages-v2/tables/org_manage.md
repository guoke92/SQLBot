---
type: table
title: 机构管理
page_key: org_manage
domain: 数据权限与组织
status: draft
anchors: [org_manage]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












org_manage 是租户级机构表，与客户组织架构（sys_cust_org、sys_cust_org_rel）是两条不同链路，同名「组织/机构」不可互推，判别见 concept [[org]]。其 org_type 写值来自 OrgTypeEnum（ORG 根 / SUB 子），status 为 varchar(10)，本链路未见写值点。

## 需求背景
本页仅依据代码证据（OrgTypeEnum）与库证据（org_manage）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

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