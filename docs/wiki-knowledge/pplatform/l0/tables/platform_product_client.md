---
type: table
title: 平台产品端口配置
page_key: platform_product_client
belong: tables
status: draft
aliases: []
anchors:
- platform_product_client
sources:
- database_schema:lowcode_pplatform.platform_product_client
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 平台产品端口配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_info

`name`, `platform_product_id`, `url`

### client_config

`client_type`, `status`, `multiple_type`, `wx_flag`, `link_type`

### ext_config

`ext_config`, `remark`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: platform_product_client
database: lowcode_pplatform
description: 平台产品端口配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: product_info
  title: 产品标识与地址
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
- key: client_config
  title: 客户端与展示配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
- key: ext_config
  title: 扩展配置与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
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
  cluster: product_info
- name: platform_product_id
  data_type: number
  description: 平台产品id
  nullable: true
  cluster: product_info
- name: url
  data_type: string
  description: 产品url
  nullable: true
  cluster: product_info
- name: client_type
  data_type: string
  description: 客户端类型方式
  nullable: true
  cluster: client_config
  dictionary: platform_product_client_client_type
- name: status
  data_type: string
  description: 启用状态
  nullable: true
  cluster: client_config
- name: multiple_type
  data_type: string
  description: 过滤类型
  nullable: true
  cluster: client_config
  dictionary: platform_product_client_multiple_type
- name: ext_config
  data_type: string
  description: 其他配置信息
  nullable: true
  cluster: ext_config
- name: wx_flag
  data_type: string
  description: 是否小程序
  nullable: true
  cluster: client_config
  dictionary: platform_product_client_wx_flag
- name: link_type
  data_type: string
  description: 链接类型(iframe/redirect/forward)
  nullable: true
  cluster: client_config
  dictionary: platform_product_client_link_type
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: ext_config
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: platform_product_client.platform_product_id
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.platform_product_client.platform_product_id
```
