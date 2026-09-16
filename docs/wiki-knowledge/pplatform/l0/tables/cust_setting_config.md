---
type: table
title: 客户认证配置
page_key: cust_setting_config
belong: tables
status: draft
aliases: []
anchors:
- cust_setting_config
sources:
- database_schema:lowcode_pplatform.cust_setting_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户认证配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### base

`name`, `remark`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### org

`organization_id`, `cust_id`

### enterprise_key

`key_word`, `no_key_word`

### agreement

`user_agreement`, `privacy_policy_agreement`, `authorization_online`, `authorization_offline`, `authorization_change`, `cfca_agreement`

### verification

`need_verify_no_key`, `need_auth_verify`, `face_recognition`

### payment

`payment_verification`, `payment_maximum_number`

### invitation

`invitation_code_period`, `invitation_code_period_unit`, `sending_interval`, `sending_interval_unti`

## 字段

```ground:table
table: cust_setting_config
database: lowcode_pplatform
description: 客户认证配置
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
- key: base
  title: 配置信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: approval
  title: 流程审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: org
  title: 企业/机构标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: enterprise_key
  title: 企业关键信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: agreement
  title: 协议签署
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: verification
  title: 认证审核
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: payment
  title: 打款验证
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
- key: invitation
  title: 邀请码
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_setting_config
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
  description: 配置名称
  nullable: true
  cluster: base
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_setting_config_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: base
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
  cluster: approval
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
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: org
- name: key_word
  data_type: string
  description: 企业关键信息
  nullable: true
  cluster: enterprise_key
- name: need_verify_no_key
  data_type: string
  description: 企业非关键信息变更审核
  nullable: true
  cluster: verification
  dictionary: cust_setting_config_need_verify_no_key
- name: user_agreement
  data_type: string
  description: 用户协议
  nullable: true
  cluster: agreement
- name: privacy_policy_agreement
  data_type: string
  description: 隐私政策
  nullable: true
  cluster: agreement
- name: authorization_online
  data_type: string
  description: 授权确认书-线上签署
  nullable: true
  cluster: agreement
- name: authorization_offline
  data_type: string
  description: 授权确认书-线下签署
  nullable: true
  cluster: agreement
- name: authorization_change
  data_type: string
  description: 数字证书服务协议
  nullable: true
  cluster: agreement
- name: cfca_agreement
  data_type: string
  description: 数字证书服务协议
  nullable: true
  cluster: agreement
- name: need_auth_verify
  data_type: string
  description: 企业认证审核
  nullable: true
  cluster: verification
  dictionary: cust_setting_config_need_auth_verify
- name: face_recognition
  data_type: string
  description: 人脸识别
  nullable: true
  cluster: verification
  dictionary: cust_setting_config_face_recognition
- name: payment_verification
  data_type: string
  description: 打款验证
  nullable: true
  cluster: payment
  dictionary: cust_setting_config_payment_verification
- name: payment_maximum_number
  data_type: number
  description: 最多申请打款次数
  nullable: true
  cluster: payment
- name: no_key_word
  data_type: string
  description: 企业非关键信息配置
  nullable: true
  cluster: enterprise_key
- name: invitation_code_period
  data_type: number
  description: 邀请码有效期
  nullable: true
  cluster: invitation
- name: invitation_code_period_unit
  data_type: string
  description: 邀请码有效期单位
  nullable: true
  cluster: invitation
- name: sending_interval
  data_type: number
  description: 邀请码重复发送时间间隔
  nullable: true
  cluster: invitation
- name: sending_interval_unti
  data_type: string
  description: 邀请码重复发送时间间隔单位
  nullable: true
  cluster: invitation
- name: cust_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: org
```
