---
type: table
title: tenant_product（租户产品开通表）
page_key: table.tenant_product
domain: 平台内部服务对接
status: draft
aliases:
  - tenant_product
  - 租户产品表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_product]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


记录某租户开通了哪些平台产品，以及这些产品是否已完成迁移。

## 需求背景

产品编码与 [[tables/platform_product]] 的 product_code 对齐（见 [[concepts/product_code_bridge]]），项目层实体见 [[tables/tenant_project]]；迁移标识与租户级 is_stack 的语义相关（见 [[calibers/tenant_stack_migratory]]）。

## 版本演进

v0：首次成页。

```ground:table
table: tenant_product
database: lowcode_pplatform
desc: 租户产品配置
fields:
  - name: id
    type: number
    desc: 表主键
  - name: open_status
    type: string
    desc: 产品开通状态
    dict: tenant_interworking_product__open_status
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
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: credit_measures
    type: string
    desc: 增信措施
  - name: customer_group
    type: string
    desc: 客户群体
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: is_migratory
    type: string
    desc: 是否迁移标识,N代表未迁移,Y代表迁移
  - name: logo_icon_url
    type: string
    desc: 产品logo
  - name: max_financing_amount
    type: string
    desc: 融资金额上限
  - name: max_financing_amount_flag
    type: string
    desc: 是否限额融资资金上线
  - name: max_financing_period
    type: string
    desc: 融资期限上限
  - name: multiple
    type: string
    desc: 是否多个
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_product_code
    type: string
    desc: 平台产品编号
  - name: platform_product_id
    type: number
    desc: 平台产品id
  - name: product_agreement
    type: string
    desc: 产品协议
  - name: product_cate
    type: string
    desc: 产品类型
  - name: product_description
    type: string
    desc: 产品详细描述
  - name: product_summary
    type: string
    desc: 产品概述
  - name: product_web_url
    type: string
    desc: 站点url
  - name: ref_tenant_product_project_code
    type: string
    desc: 租户产品-平台产品
  - name: ref_tenant_product_tenant_setting_config
    type: string
    desc: 租户-产品
  - name: remark
    type: string
    desc: remark
  - name: tenant_id
    type: number
    desc: 租户id
  - name: transaction_structure
    type: string
    desc: 交易结构
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
  - name: view_order
    type: number
    desc: 展示顺序
```
## 关联表

- [[cust_auth_application]]：tenant_product.code → cust_auth_application.ref_cust_auth_application_tenant_product（ref-convention:CustAuthApplicationDO.java，suggested）
- [[cust_project_rel]]：tenant_product.platform_product_id → cust_project_rel.product_id（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[platform_product]]：tenant_product.ref_tenant_product_project_code → platform_product.code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_project]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_project.ref_tenant_project_tenant_code（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_setting_config]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantProductDO.java，suggested）
