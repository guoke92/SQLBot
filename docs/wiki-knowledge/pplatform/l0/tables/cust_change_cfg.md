---
type: table
title: 客户变更配置
page_key: cust_change_cfg
belong: tables
status: draft
aliases: []
anchors:
- cust_change_cfg
sources:
- database_schema:lowcode_pplatform.cust_change_cfg
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户变更配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### change_item

`name`, `plat_item`, `oper_item`, `item_code`

### customer_flow

`cust_type`, `identify_style`, `head_company`, `open_process`, `client_type`

### desc

`data_desc`, `remark`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
description: 客户变更配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- item_code
clusters:
- key: common
  title: 通用
  include: always
- key: change_item
  title: 变更项配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: customer_flow
  title: 客户与流程属性
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: desc
  title: 说明备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: workflow
  title: 流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: tenant_org
  title: 租户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
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
  cluster: change_item
- name: plat_item
  data_type: string
  description: 平台变更项
  nullable: true
  cluster: change_item
- name: oper_item
  data_type: string
  description: 运营中台变更项
  nullable: true
  cluster: change_item
- name: data_desc
  data_type: string
  description: 变更需要材料说明
  nullable: true
  cluster: desc
- name: cust_type
  data_type: string
  description: 客户类型
  nullable: true
  cluster: customer_flow
  dictionary: cust_change_cfg_cust_type
- name: identify_style
  data_type: string
  description: 认证方式
  nullable: true
  cluster: customer_flow
  dictionary: cust_change_cfg_identify_style
- name: head_company
  data_type: string
  description: 是否总公司
  nullable: true
  cluster: customer_flow
  dictionary: cust_change_cfg_head_company
- name: open_process
  data_type: string
  description: 开启流程
  nullable: true
  cluster: customer_flow
  dictionary: cust_change_cfg_open_process
- name: item_code
  data_type: string
  description: 变更项编码
  nullable: true
  cluster: change_item
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: desc
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
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_org
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
  cluster: tenant_org
- name: client_type
  data_type: string
  description: 端类型
  nullable: true
  cluster: customer_flow
  dictionary: cust_change_cfg_client_type
```
