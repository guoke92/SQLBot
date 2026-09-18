---
type: table
title: 客戶sftp信息
page_key: cust_sftp
belong: tables
status: draft
anchors: [cust_sftp]
sources: ['database_schema:lowcode_pplatform.cust_sftp']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_sftp__enable, cust_sftp__channel]
---

# 客戶sftp信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`

### sftp_access

`host`, `port`, `user_name`, `password`, `private_key`, `private_key_pwd`

### tenant

`app_tenant_code`, `db_tenant_code`

### procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### org_channel

`organization_id`, `channel`

## 字段

```ground:table
table: cust_sftp
database: lowcode_pplatform
description: 客戶sftp信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, user_name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 客户身份
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: sftp_access
  title: SFTP连接配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: tenant
  title: 租户隔离
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: org_channel
  title: 机构与渠道
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
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
- name: host
  data_type: string
  description: 服务器地址IP地址
  cluster: sftp_access
- name: port
  data_type: number
  description: 端口
  cluster: sftp_access
- name: user_name
  data_type: string
  description: 登录用户名
  cluster: sftp_access
- name: password
  data_type: string
  description: 登录密码
  cluster: sftp_access
- name: private_key
  data_type: string
  description: 私钥
  cluster: sftp_access
- name: private_key_pwd
  data_type: string
  description: 私钥的密码
  cluster: sftp_access
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_sftp__enable
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
  cluster: procinst
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
  cluster: procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: org_channel
- name: channel
  data_type: string
  description: 渠道
  cluster: org_channel
  dictionary: cust_sftp__channel
```

## 页面链接

### 字典

- [[dicts/cust_sftp__enable]]（`cust_sftp.enable`）
- [[dicts/cust_sftp__channel]]（`cust_sftp.channel`）
