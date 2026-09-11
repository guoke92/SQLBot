---
type: table
title: 租户产品菜单表（tenant_product_menu）
page_key: tables/tenant_product_menu
domain: 租户产品
status: draft
aliases: [tenant_product_menu, 租户产品菜单表]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product_menu
contract_version: "0.1"
---


租户产品菜单表按「产品 code × 企业角色」登记可用的菜单项，是租户产品开通后前台可见性的配置载体。与 [[tables/tenant_product_menu_res]] 的区别在于本表按 menu_id 关联产品菜单，而后者面向数据租户维度的菜单资源。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表解决的是「同一产品在不同企业角色下应看到哪些菜单」的配置问题，企业角色的取值口径见 [[calibers/company_type]]。

## 版本演进
- enable 列 DB 实测均为 Y，属恒定量，未观察到关闭态样本。
- product_code 的 DB 实测值 ACCOUNT_PRODUCT/BEECREDIT/RVSFACTOR_PC 与 [[tables/tenant_product]] 的 platform_product_code 值域不完全一致，ACCOUNT_PRODUCT 未出现在该表实测值中。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_product_menu
database: lowcode_pplatform
desc: 租户产品菜单表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: company_type
    type: string
    desc: 企业角色
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: menu_id
    type: number
    desc: 菜单id
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: product_code
    type: string
    desc: 产品code
  - name: remark
    type: string
    desc: remark
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

启用的口径统一见 [[calibers/product_enable_flag]]。