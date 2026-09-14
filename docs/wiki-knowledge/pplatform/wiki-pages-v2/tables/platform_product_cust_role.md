---
type: table
title: 平台产品企业角色
page_key: platform_product_cust_role
domain: 客户角色与端口
status: draft
anchors: [platform_product_cust_role]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












platform_product_cust_role 定义某个产品下支持哪些企业角色，即业务口语中的“端口”。company_type_code 与 [[cust_role_info]].role_type 共用编码（CORE、SUPPLIER、FINANCE 等），二者为逻辑关联（derived，无外键约束）。术语见 [[port]]、[[company_role]]。

## 需求背景

产品开通时，产品下可支持的企业角色决定了客户能选择的端口集合；菜单配置需要按端口逐个勾选，形成 tenant_product_menu 配置（见 [[menu_port_filter]]）。因此本表是「客户角色」与「菜单可见性」之间的桥接表，也是 [[valid_product_cust_role]] 口径的事实来源。

## 版本演进

- v0（draft）：基于 db 字段语义与 LocalTypeMenuService 代码路径首次成页。

```ground:table
table: platform_product_cust_role
database: lowcode_pplatform
desc: 平台产品企业角色
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_type_code
    type: string
    phys: varchar(32)
    desc: 企业角色编码
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
  - name: company_type_name
    type: string
    phys: varchar(128)
    desc: 企业角色名称
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
    phys: varchar(128)
    desc: 产品编码
    topk: "ACCOUNT_PRODUCT|ACFLOW|AMS|BEECREDIT|CROSSBORDER|DEALER|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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