---
type: table
title: platform_product（平台产品表）
page_key: table.platform_product
domain: 平台内部服务对接
status: draft
aliases:
  - platform_product
  - 平台产品表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[platform_product]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


平台侧产品字典表，提供产品编码与名称，是项目列表展示与租户产品开通的对照基准。

## 需求背景

产品编码在多个关系表中以不同列名出现（platform_product_code、ref_cust_project_rel_platform_product），统一口径见 [[concepts/product_code_bridge]]。

## 版本演进

v0：首次成页。

```ground:table
table: platform_product
database: lowcode_pplatform
desc: 平台产品基础配置
fields:
  - name: id
    type: number
    desc: 表主键
  - name: product_status
    type: string
    desc: 产品状态
    dict: product_status
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
  - name: app_code
    type: string
    desc: 蜂搭平台app编号
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: basic_product
    type: string
    desc: 是否是产融底座
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
  - name: cust_role_combine
    type: string
    desc: 支持企业角色组合
  - name: customer_group
    type: string
    desc: 客户群体
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: default_menu_code
    type: string
    desc: 默认菜单编号
  - name: default_menu_index
    type: number
    desc: 默认菜单编号
  - name: enable
    type: string
    desc: enable
  - name: general_flag
    type: string
    desc: 通用产品标识
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
  - name: menu_type
    type: string
    desc: 菜单展示类型(topLeft/left)
  - name: multiple_client_type
    type: string
    desc: 多端口类型
  - name: multiple_cust_role_flag
    type: string
    desc: 是否有多企业角色
  - name: multiple_project_flag
    type: string
    desc: 是否有多项目
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_code
    type: string
    desc: 平台编码
  - name: platform_flag
    type: string
    desc: 是否平台标识
  - name: product_cate
    type: string
    desc: 产品类型
  - name: product_code
    type: string
    desc: 产品编码
  - name: product_construction_status
    type: string
    desc: 产品建设情况
  - name: product_description
    type: string
    desc: 产品详细描述
  - name: product_ref_num
    type: number
    desc: 引用产品的平台数
  - name: product_summary
    type: string
    desc: 产品概述
  - name: product_type
    type: string
    desc: 通用产品标识
  - name: project_code
    type: string
    desc: 蜂搭平台项目编号
  - name: project_config
    type: string
    desc: 项目配置
  - name: remark
    type: string
    desc: remark
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
  - name: wkfl_flag
    type: string
    desc: 产品工作流启用开关
```
## 关联表

- [[cust_project_rel]]：platform_product.code → cust_project_rel.ref_cust_project_rel_platform_product（ref-convention:CustProjectRelDO.java，suggested）
- [[tenant_interworking_product]]：platform_product.code → tenant_interworking_product.ref_tenant_interworking_product_platform_product（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_product]]：platform_product.code → tenant_product.ref_tenant_product_project_code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_project]]：platform_product.code → tenant_project.ref_tenant_project_platform_product（ref-convention:TenantProjectDO.java，suggested）
