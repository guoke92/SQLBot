---
type: table
title: 客户变更配置
page_key: cust_change_cfg
belong: tables
status: draft
anchors: [cust_change_cfg]
sources: ['database_schema:lowcode_pplatform.cust_change_cfg']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_change_record, cust_change_cfg__cust_type, cust_change_cfg__identify_style,
  cust_change_cfg__head_company, cust_change_cfg__open_process, cust_change_cfg__item_code,
  cust_change_cfg__enable, cust_change_cfg__client_type]
---

# 客户变更配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### change_item

`plat_item`, `oper_item`, `data_desc`, `item_code`

### customer

`cust_type`, `identify_style`, `head_company`, `organization_id`, `client_type`

### process

`open_process`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
description: 客户变更配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, item_code]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: change_item
  title: 变更项定义
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: customer
  title: 客户与机构属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: process
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_cfg
- key: tenant
  title: 租户标识
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: plat_item
  data_type: string
  description: 平台变更项
  cluster: change_item
- name: oper_item
  data_type: string
  description: 运营中台变更项
  cluster: change_item
- name: data_desc
  data_type: string
  description: 变更需要材料说明
  cluster: change_item
- name: cust_type
  data_type: string
  description: 客户类型
  cluster: customer
  dictionary: cust_change_cfg__cust_type
- name: identify_style
  data_type: string
  description: 认证方式
  cluster: customer
  dictionary: cust_change_cfg__identify_style
- name: head_company
  data_type: string
  description: 是否总公司
  cluster: customer
  dictionary: cust_change_cfg__head_company
- name: open_process
  data_type: string
  description: 开启流程
  cluster: process
  dictionary: cust_change_cfg__open_process
- name: item_code
  data_type: string
  description: 变更项编码
  cluster: change_item
  dictionary: cust_change_cfg__item_code
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_change_cfg__enable
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
  cluster: process
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
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: customer
- name: client_type
  data_type: string
  description: 端类型
  cluster: customer
  dictionary: cust_change_cfg__client_type
```

## 页面链接

### 关联表

- [[tables/cust_change_record]]

### 字典

- [[dicts/cust_change_cfg__cust_type]]（`cust_change_cfg.cust_type`）
- [[dicts/cust_change_cfg__identify_style]]（`cust_change_cfg.identify_style`）
- [[dicts/cust_change_cfg__head_company]]（`cust_change_cfg.head_company`）
- [[dicts/cust_change_cfg__open_process]]（`cust_change_cfg.open_process`）
- [[dicts/cust_change_cfg__item_code]]（`cust_change_cfg.item_code`）
- [[dicts/cust_change_cfg__enable]]（`cust_change_cfg.enable`）
- [[dicts/cust_change_cfg__client_type]]（`cust_change_cfg.client_type`）
