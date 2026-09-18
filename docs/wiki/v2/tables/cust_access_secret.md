---
type: table
title: 客户接入秘钥信息
page_key: cust_access_secret
belong: tables
status: draft
anchors: [cust_access_secret]
sources: ['database_schema:lowcode_pplatform.cust_access_secret']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_access_secret__channel, cust_access_secret__encry_type, cust_access_secret__enable,
  cust_access_secret__status_query_license_enabled]
---

# 客户接入秘钥信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`, `channel`, `organization_id`

### key_material

`encry_type`, `pub_key`, `pri_key`, `password`, `key_num`, `rel_lls_secret_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`status_query_license_enabled`

## 字段

```ground:table
table: cust_access_secret
database: lowcode_pplatform
description: 客户接入秘钥信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 客户与应用标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: key_material
  title: 密钥材料
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_access_secret
- key: approval
  title: 审批流程
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: channel
  data_type: string
  description: 应用id
  cluster: identity
  dictionary: cust_access_secret__channel
- name: encry_type
  data_type: string
  description: 加密类型
  cluster: key_material
  dictionary: cust_access_secret__encry_type
- name: pub_key
  data_type: string
  description: 公钥
  cluster: key_material
- name: pri_key
  data_type: string
  description: 私钥
  cluster: key_material
- name: password
  data_type: string
  description: 密码
  cluster: key_material
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_access_secret__enable
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
  cluster: identity
- name: key_num
  data_type: number
  description: 密钥对
  nullable: false
  cluster: key_material
- name: rel_lls_secret_id
  data_type: number
  description: 关联平台密钥记录id
  cluster: key_material
- name: status_query_license_enabled
  data_type: string
  description: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
  dictionary: cust_access_secret__status_query_license_enabled
```

## 页面链接

### 字典

- [[dicts/cust_access_secret__channel]]（`cust_access_secret.channel`）
- [[dicts/cust_access_secret__encry_type]]（`cust_access_secret.encry_type`）
- [[dicts/cust_access_secret__enable]]（`cust_access_secret.enable`）
- [[dicts/cust_access_secret__status_query_license_enabled]]（`cust_access_secret.status_query_license_enabled`）
