---
type: table
title: 平台产品基础配置
page_key: platform_product
belong: tables
status: draft
aliases: []
anchors:
- platform_product
sources:
- database_schema:lowcode_pplatform.platform_product
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 平台产品基础配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### product_profile

`name`, `product_type`, `product_code`, `product_cate`, `product_summary`, `product_description`, `customer_group`, `product_ref_num`, `product_status`, `product_construction_status`, `basic_product`, `logo_icon_url`, `general_flag`

### platform

`platform_flag`, `platform_code`

### multiple

`multiple_project_flag`, `multiple_cust_role_flag`, `multiple_client_type`, `cust_role_combine`

### financing

`max_financing_period`, `max_financing_amount`, `credit_measures`, `transaction_structure`, `max_financing_amount_flag`

### project

`project_code`, `app_code`, `organization_id`, `project_config`

### workflow

`wkfl_flag`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### menu

`menu_type`, `default_menu_code`, `default_menu_index`

### 未归簇

`remark`

## 字段

```ground:table
table: platform_product
database: lowcode_pplatform
description: 平台产品基础配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- platform_code
- product_code
- project_code
- app_code
- default_menu_code
clusters:
- key: common
  title: 通用/审计
  include: always
- key: product_profile
  title: 产品主档信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: platform
  title: 平台标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: multiple
  title: 多项目/多角色配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: financing
  title: 融资要素
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: project
  title: 项目与外部关联编号
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: menu
  title: 菜单展示配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: product_profile
- name: product_type
  data_type: string
  description: 通用产品标识
  nullable: true
  cluster: product_profile
  dictionary: platform_product_product_type
- name: platform_flag
  data_type: string
  description: 是否平台标识
  nullable: true
  cluster: platform
  dictionary: platform_product_platform_flag
- name: platform_code
  data_type: string
  description: 平台编码
  nullable: true
  cluster: platform
- name: multiple_project_flag
  data_type: string
  description: 是否有多项目
  nullable: true
  cluster: multiple
  dictionary: platform_product_multiple_project_flag
- name: multiple_cust_role_flag
  data_type: string
  description: 是否有多企业角色
  nullable: true
  cluster: multiple
  dictionary: platform_product_multiple_cust_role_flag
- name: product_code
  data_type: string
  description: 产品编码
  nullable: true
  cluster: product_profile
- name: product_cate
  data_type: string
  description: 产品类型
  nullable: true
  cluster: product_profile
  dictionary: platform_product_product_cate
- name: product_summary
  data_type: string
  description: 产品概述
  nullable: true
  cluster: product_profile
- name: product_description
  data_type: string
  description: 产品详细描述
  nullable: true
  cluster: product_profile
- name: customer_group
  data_type: string
  description: 客户群体
  nullable: true
  cluster: product_profile
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  nullable: true
  cluster: financing
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  nullable: true
  cluster: financing
- name: credit_measures
  data_type: string
  description: 增信措施
  nullable: true
  cluster: financing
- name: transaction_structure
  data_type: string
  description: 交易结构
  nullable: true
  cluster: financing
- name: product_ref_num
  data_type: number
  description: 引用产品的平台数
  nullable: true
  cluster: product_profile
- name: product_status
  data_type: string
  description: 产品状态
  nullable: true
  cluster: product_profile
- name: product_construction_status
  data_type: string
  description: 产品建设情况
  nullable: true
  cluster: product_profile
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上线
  nullable: true
  cluster: financing
  dictionary: platform_product_max_financing_amount_flag
- name: multiple_client_type
  data_type: string
  description: 多端口类型
  nullable: true
  cluster: multiple
- name: project_code
  data_type: string
  description: 蜂搭平台项目编号
  nullable: true
  cluster: project
- name: app_code
  data_type: string
  description: 蜂搭平台app编号
  nullable: true
  cluster: project
- name: basic_product
  data_type: string
  description: 是否是产融底座
  nullable: true
  cluster: product_profile
- name: menu_type
  data_type: string
  description: 菜单展示类型(topLeft/left)
  nullable: true
  cluster: menu
  dictionary: platform_product_menu_type
- name: default_menu_code
  data_type: string
  description: 默认菜单编号
  nullable: true
  cluster: menu
- name: default_menu_index
  data_type: number
  description: 默认菜单编号
  nullable: true
  cluster: menu
- name: wkfl_flag
  data_type: string
  description: 产品工作流启用开关
  nullable: true
  cluster: workflow
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: platform_product_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: project
- name: logo_icon_url
  data_type: string
  description: 产品logo
  nullable: true
  cluster: product_profile
- name: cust_role_combine
  data_type: string
  description: 支持企业角色组合
  nullable: true
  cluster: multiple
- name: general_flag
  data_type: string
  description: 通用产品标识
  nullable: true
  cluster: product_profile
- name: project_config
  data_type: string
  description: 项目配置
  nullable: true
  cluster: project
```
