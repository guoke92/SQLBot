---
type: table
title: 企业信息配置表
page_key: cust_config_mapping
belong: tables
status: draft
anchors: [cust_config_mapping]
sources: ['database_schema:lowcode_pplatform.cust_config_mapping']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_config_mapping__outer_channel, cust_config_mapping__inner_code, cust_config_mapping__outer_code,
  cust_config_mapping__type, cust_config_mapping__groups, cust_config_mapping__enable,
  cust_config_mapping__db_tenant_code]
---

# 企业信息配置表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### mapping

`outer_channel`, `inner_code`, `inner_name`, `outer_code`, `outer_name`, `type`, `groups`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`organization_id`

## 字段

```ground:table
table: cust_config_mapping
database: lowcode_pplatform
description: 企业信息配置表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, inner_code, inner_name, outer_code, outer_name]
clusters:
- key: common
  title: 通用
  include: always
- key: mapping
  title: 内外码映射配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_config_mapping
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_config_mapping
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
- name: outer_channel
  data_type: string
  description: 外部渠道
  cluster: mapping
  dictionary: cust_config_mapping__outer_channel
- name: inner_code
  data_type: string
  description: 内部编码
  cluster: mapping
  dictionary: cust_config_mapping__inner_code
- name: inner_name
  data_type: string
  description: 内部名称
  cluster: mapping
- name: outer_code
  data_type: string
  description: 外部编码
  cluster: mapping
  dictionary: cust_config_mapping__outer_code
- name: outer_name
  data_type: string
  description: 外部名称
  cluster: mapping
- name: type
  data_type: string
  description: 类型
  cluster: mapping
  dictionary: cust_config_mapping__type
- name: groups
  data_type: string
  description: 分组
  cluster: mapping
  dictionary: cust_config_mapping__groups
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_config_mapping__enable
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
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
  dictionary: cust_config_mapping__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
```

## 页面链接

### 字典

- [[dicts/cust_config_mapping__outer_channel]]（`cust_config_mapping.outer_channel`）
- [[dicts/cust_config_mapping__inner_code]]（`cust_config_mapping.inner_code`）
- [[dicts/cust_config_mapping__outer_code]]（`cust_config_mapping.outer_code`）
- [[dicts/cust_config_mapping__type]]（`cust_config_mapping.type`）
- [[dicts/cust_config_mapping__groups]]（`cust_config_mapping.groups`）
- [[dicts/cust_config_mapping__enable]]（`cust_config_mapping.enable`）
- [[dicts/cust_config_mapping__db_tenant_code]]（`cust_config_mapping.db_tenant_code`）
