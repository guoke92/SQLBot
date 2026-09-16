---
type: table
title: 短链接
page_key: short_link
belong: tables
status: draft
aliases: []
anchors:
- short_link
sources:
- database_schema:lowcode_pplatform.short_link
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 短链接

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### link_content

`name`, `source_url`, `number`

### expire_rule

`expire_time`, `type`, `is_forever`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

### 未归簇

`remark`

## 字段

```ground:table
table: short_link
database: lowcode_pplatform
description: 短链接
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: link_content
  title: 短链内容
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.short_link
- key: expire_rule
  title: 有效期规则
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.short_link
- key: act_procinst
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.short_link
- key: tenant_org
  title: 租户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.short_link
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
  cluster: link_content
- name: source_url
  data_type: string
  description: 源链接
  nullable: true
  cluster: link_content
- name: expire_time
  data_type: temporal
  description: 到期时间
  nullable: true
  cluster: expire_rule
- name: number
  data_type: string
  description: 编码
  nullable: true
  cluster: link_content
- name: type
  data_type: string
  description: 类型
  nullable: true
  cluster: expire_rule
  dictionary: short_link_type
- name: is_forever
  data_type: string
  description: 到期类型
  nullable: true
  cluster: expire_rule
  dictionary: short_link_is_forever
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
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
  cluster: act_procinst
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
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_org
```
