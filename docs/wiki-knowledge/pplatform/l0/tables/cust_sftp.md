---
type: table
title: 客戶sftp信息
page_key: cust_sftp
belong: tables
status: draft
aliases: []
anchors:
- cust_sftp
sources:
- database_schema:lowcode_pplatform.cust_sftp
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客戶sftp信息

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### basic

`name`, `remark`

### conn

`host`, `port`, `user_name`

### cred

`password`, `private_key`, `private_key_pwd`

### tenant

`app_tenant_code`, `db_tenant_code`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### owner

`organization_id`, `channel`

## 字段

```ground:table
table: cust_sftp
database: lowcode_pplatform
description: 客戶sftp信息
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- user_name
clusters:
- key: common
  title: 通用/审计与主键
  include: always
- key: basic
  title: SFTP 主档基础信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: conn
  title: 连接参数
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: cred
  title: 凭证与密钥
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: workflow
  title: 流程审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_sftp
- key: owner
  title: 归属机构与渠道
  confidence: proposed
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
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: basic
- name: host
  data_type: string
  description: 服务器地址IP地址
  nullable: true
  cluster: conn
- name: port
  data_type: number
  description: 端口
  nullable: true
  cluster: conn
- name: user_name
  data_type: string
  description: 登录用户名
  nullable: true
  cluster: conn
- name: password
  data_type: string
  description: 登录密码
  nullable: true
  cluster: cred
- name: private_key
  data_type: string
  description: 私钥
  nullable: true
  cluster: cred
- name: private_key_pwd
  data_type: string
  description: 私钥的密码
  nullable: true
  cluster: cred
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_sftp_enable
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
  cluster: workflow
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
  cluster: owner
- name: channel
  data_type: string
  description: 渠道
  nullable: true
  cluster: owner
  dictionary: cust_sftp_channel
```
