---
type: table
title: 客户接入秘钥信息
page_key: cust_access_secret
belong: tables
status: draft
aliases: []
anchors:
- cust_access_secret
sources:
- database_schema:lowcode_pplatform.cust_access_secret
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户接入秘钥信息

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### basic

`name`, `remark`

### crypto

`encry_type`, `pub_key`, `pri_key`, `password`, `key_num`, `rel_lls_secret_id`

### access

`channel`, `status_query_license_enabled`

### tenant

`app_tenant_code`, `db_tenant_code`, `organization_id`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: cust_access_secret
database: lowcode_pplatform
description: 客户接入秘钥信息
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
- key: basic
  title: 名称与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: crypto
  title: 密钥材料与关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: access
  title: 接入渠道
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: tenant
  title: 租户与机构归属
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: act_procinst
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
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
  cluster: basic
- name: channel
  data_type: string
  description: 应用id
  nullable: true
  cluster: access
- name: encry_type
  data_type: string
  description: 加密类型
  nullable: true
  cluster: crypto
- name: pub_key
  data_type: string
  description: 公钥
  nullable: true
  cluster: crypto
- name: pri_key
  data_type: string
  description: 私钥
  nullable: true
  cluster: crypto
- name: password
  data_type: string
  description: 密码
  nullable: true
  cluster: crypto
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_access_secret_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: basic
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
  cluster: tenant
- name: key_num
  data_type: number
  description: 密钥对
  nullable: false
  cluster: crypto
- name: rel_lls_secret_id
  data_type: number
  description: 关联平台密钥记录id
  nullable: true
  cluster: crypto
- name: status_query_license_enabled
  data_type: string
  description: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
  nullable: true
  cluster: access
  dictionary: cust_access_secret_status_query_license_enabled
```
