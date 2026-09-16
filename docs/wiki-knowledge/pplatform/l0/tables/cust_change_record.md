---
type: table
title: 客户变更记录
page_key: cust_change_record
belong: tables
status: draft
aliases: []
anchors:
- cust_change_record
sources:
- database_schema:lowcode_pplatform.cust_change_record
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户变更记录

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### cust

`cust_id`, `cust_name`, `cust_type`, `pp_cust_info`, `cust_company_type`

### alter

`alter_data`, `alter_mode`, `alter_type`, `status`, `alter_type_id`

### oper

`oper_app_no`, `oper_cust_info`, `oper_cust_id`, `oper_channel`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### auth

`admin_auth`, `legal_auth`, `electronic_auth_sign_status`

### need

`msg_send`, `need_cust_confirm`, `need_resign_auth`

### misc

`name`, `remark`, `organization_id`

## 字段

```ground:table
table: cust_change_record
database: lowcode_pplatform
description: 客户变更记录
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- cust_name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: cust
  title: 客户主体信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: alter
  title: 变更内容与类型
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: oper
  title: 运营中台信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: act_procinst
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: auth
  title: 授权与签署
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: need
  title: 变更要求与通知
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: misc
  title: 记录描述与归属
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
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
  cluster: misc
- name: cust_id
  data_type: number
  description: 客户记录id
  nullable: true
  cluster: cust
- name: cust_name
  data_type: string
  description: 客户名称
  nullable: true
  cluster: cust
- name: alter_data
  data_type: string
  description: 变更数据
  nullable: true
  cluster: alter
- name: alter_mode
  data_type: string
  description: 变更方式
  nullable: true
  cluster: alter
  dictionary: cust_change_record_alter_mode
- name: admin_auth
  data_type: string
  description: 企业管理授权
  nullable: true
  cluster: auth
  dictionary: cust_change_record_admin_auth
- name: legal_auth
  data_type: string
  description: 法人代表授权
  nullable: true
  cluster: auth
  dictionary: cust_change_record_legal_auth
- name: alter_type
  data_type: string
  description: 变更类型
  nullable: true
  cluster: alter
- name: cust_type
  data_type: string
  description: 客户类型
  nullable: true
  cluster: cust
- name: oper_app_no
  data_type: string
  description: 运营中台流程编号
  nullable: true
  cluster: oper
- name: oper_cust_info
  data_type: string
  description: 运营中台客户信息
  nullable: true
  cluster: oper
- name: pp_cust_info
  data_type: string
  description: 产融客户信息
  nullable: true
  cluster: cust
- name: status
  data_type: string
  description: 变更状态
  nullable: true
  cluster: alter
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_change_record_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: misc
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
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: common
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
  cluster: misc
- name: oper_cust_id
  data_type: number
  description: 运营中台客户id
  nullable: true
  cluster: oper
- name: cust_company_type
  data_type: string
  description: 客户企业类型
  nullable: true
  cluster: cust
  dictionary: cust_change_record_cust_company_type
- name: alter_type_id
  data_type: string
  description: 变更项记录id
  nullable: true
  cluster: alter
- name: msg_send
  data_type: string
  description: 消息发送
  nullable: true
  cluster: need
  dictionary: cust_change_record_msg_send
- name: need_cust_confirm
  data_type: string
  description: 是否需要客户确认
  nullable: true
  cluster: need
  dictionary: cust_change_record_need_cust_confirm
- name: need_resign_auth
  data_type: string
  description: 是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读
  nullable: true
  cluster: need
  dictionary: cust_change_record_need_resign_auth
- name: oper_channel
  data_type: string
  description: 运营中台变更渠道
  nullable: true
  cluster: oper
  dictionary: cust_change_record_oper_channel
- name: electronic_auth_sign_status
  data_type: string
  description: ''
  nullable: true
  cluster: auth
  dictionary: cust_change_record_electronic_auth_sign_status
```
