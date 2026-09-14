---
type: table
title: 租户产品菜单按钮表
page_key: tenant_product_menu_res
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_product_menu_res]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---
















租户产品菜单资源表按「产品 code × 企业角色 × 数据租户」登记菜单资源，是本主题中唯一显式带 db_tenant_code 的菜单类配置表，因而承担了菜单配置的租户隔离维度。与 [[tables/tenant_product_menu]] 配合使用。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。证据显示本表要解决的是「同一个产品与角色组合，在不同数据租户下菜单资源可以不同」的问题；数据租户标识的含义见 [[concepts/logical_vs_db_tenant_code]]。

## 版本演进
- db_tenant_code 的 DB 实测值为 LN1/beehive-scf.qhhrly.cn/ning，取值形态包含简码与域名，属于历史遗留的混合命名。
- enable 列 DB 实测均为 Y。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_product_menu_res
database: lowcode_pplatform
desc: 租户产品菜单按钮表
fields:
  - name: company_type
    type: string
    phys: varchar(32)
    desc: 企业类型
    dict: tenant_product_menu_res__company_type
    topk: "CORE|CORPORATION_COMPANY|PLATFORM_OPERATOR_COMPANY|SUPPLIER"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "LN1|beehive-scf.qhhrly.cn|ning"
  - name: menu_id
    type: number
    phys: bigint(20)
    desc: 菜单ID
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_code
    type: string
    phys: varchar(64)
    desc: 产品code
    topk: "ACCOUNT_PRODUCT|RVSFACTOR_PC"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: resource_id
    type: number
    phys: bigint(20)
    desc: 按钮ID
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

企业角色口径见 [[calibers/company_type]]。