---
type: table
title: 平台产品端口配置
page_key: platform_product_client
belong: tables
status: draft
anchors: [platform_product_client]
sources: ['database_schema:lowcode_pplatform.platform_product_client']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, platform_product_client__client_type, platform_product_client__status,
  platform_product_client__multiple_type, platform_product_client__wx_flag, platform_product_client__link_type]
---

# 平台产品端口配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_access

`platform_product_id`, `url`, `client_type`, `status`, `multiple_type`, `ext_config`, `wx_flag`, `link_type`

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
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: product_access
  title: 产品接入配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_client
- key: tenant
  title: 租户隔离
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: platform_product_id
  data_type: number
  description: 平台产品id
  cluster: product_access
- name: url
  data_type: string
  description: 产品url
  cluster: product_access
- name: client_type
  data_type: string
  description: 客户端类型方式
  cluster: product_access
  dictionary: platform_product_client__client_type
- name: status
  data_type: string
  description: 启用状态
  cluster: product_access
  dictionary: platform_product_client__status
- name: multiple_type
  data_type: string
  description: 过滤类型
  cluster: product_access
  dictionary: platform_product_client__multiple_type
- name: ext_config
  data_type: string
  description: 其他配置信息
  cluster: product_access
- name: wx_flag
  data_type: string
  description: 是否小程序
  cluster: product_access
  dictionary: platform_product_client__wx_flag
- name: link_type
  data_type: string
  description: 链接类型(iframe/redirect/forward)
  cluster: product_access
  dictionary: platform_product_client__link_type
- name: enable
  data_type: string
  description: enable
  cluster: common
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: platform_product_client.platform_product_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.platform_product_client.platform_product_id;database_profile:lowcode_pplatform.platform_product_client.platform_product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 8
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/platform_product_client__client_type]]（`platform_product_client.client_type`）
- [[dicts/platform_product_client__status]]（`platform_product_client.status`）
- [[dicts/platform_product_client__multiple_type]]（`platform_product_client.multiple_type`）
- [[dicts/platform_product_client__wx_flag]]（`platform_product_client.wx_flag`）
- [[dicts/platform_product_client__link_type]]（`platform_product_client.link_type`）
