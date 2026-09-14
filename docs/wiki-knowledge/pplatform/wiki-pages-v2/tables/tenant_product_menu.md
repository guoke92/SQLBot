---
type: table
title: 租户产品菜单表
page_key: tenant_product_menu
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_product_menu]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`tenant_product_menu` 描述"某个产品在某类企业角色下可见的菜单集合"，是产品开通后前端菜单渲染的配置来源，三者组合定位一条授权：`product_code`（产品）+ `company_type`（企业角色）+ `menu_id`（菜单）。产品维度对应 [[tenant_product]] 的产品编码体系，企业角色维度与 [[cust_project_rel]] 的 `company_type` 同源。

## 需求背景
语义分析未附带需求文档锚点，依据 DB 实测值归纳：不同角色的企业（核心企业、供应商、经销商、金融机构、平台运营方、公司/项目公司）在同一产品下看到的菜单不同，因此需要按 `company_type` 差异化配置菜单。

## 版本演进
语义分析未记录该表的版本演进；`product_code` 实测值覆盖 ACCOUNT_PRODUCT/BEECREDIT/RVSFACTOR_PC，说明菜单配置随产品线扩展逐批追加。

```ground:table
table: tenant_product_menu
database: lowcode_pplatform
desc: 租户产品菜单表
fields:
  - name: company_type
    type: string
    phys: varchar(128)
    desc: 企业角色
    dict: tenant_product_menu__company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
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
  - name: menu_id
    type: number
    phys: bigint(20)
    desc: 菜单id
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
    desc: 产品code
    topk: "ACCOUNT_PRODUCT|BEECREDIT|RVSFACTOR_PC"
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