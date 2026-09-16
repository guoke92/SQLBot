---
type: table
title: 客户联系人表
page_key: cust_person_info
belong: tables
status: draft
aliases: []
anchors:
- cust_person_info
sources:
- database_schema:lowcode_pplatform.cust_person_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户联系人表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### profile

`name`, `phone`, `email`, `en_name`, `birth_date`, `en_name_end`

### certification

`certification_type`, `certification_no`, `certification_expire`, `face_status`, `realname_status`, `phone_realname_status`, `skip_auth_flag`, `real_name_result`

### account

`user_id`, `status`, `user_type`, `auth_application`, `platform_user_id`, `user_name`, `source`

### company

`organization_id`, `main_data_id`, `ref_cust_company_info`, `cust_company_id`, `company_type`, `cust_build_status`

### operator

`operator`, `operator_id`, `operator_realname`, `operator_push_system`

### handler

`handby_person`, `handby_person_name`

### misc

`test_data`, `ext_data`

## 字段

```ground:table
table: cust_person_info
database: lowcode_pplatform
description: 客户联系人表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- en_name
- handby_person_name
- user_name
clusters:
- key: common
  title: 通用
  include: always
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: process
  title: 流程审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: profile
  title: 个人基本信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: certification
  title: 认证信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: account
  title: 账号与权限
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: company
  title: 企业/客户信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: operator
  title: 运营人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: handler
  title: 经办人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: misc
  title: 扩展/测试
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
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
  description: 姓名
  nullable: true
  cluster: profile
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_person_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
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
  cluster: process
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
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: company
- name: phone
  data_type: string
  description: 手机号
  nullable: true
  cluster: profile
- name: certification_type
  data_type: string
  description: 证件类型
  nullable: true
  cluster: certification
  dictionary: cust_person_info_certification_type
- name: certification_no
  data_type: string
  description: 证件号码
  nullable: true
  cluster: certification
- name: certification_expire
  data_type: string
  description: 证件有效期
  nullable: true
  cluster: certification
- name: email
  data_type: string
  description: 邮箱
  nullable: true
  cluster: profile
- name: user_id
  data_type: number
  description: 关联用户
  nullable: true
  cluster: account
- name: main_data_id
  data_type: number
  description: 主数据id
  nullable: true
  cluster: company
- name: ref_cust_company_info
  data_type: string
  description: 关联企业
  nullable: true
  cluster: company
- name: status
  data_type: string
  description: 联系人账号状态
  nullable: true
  cluster: account
  dictionary: cust_person_info_status
- name: cust_company_id
  data_type: number
  description: 冗余企业id
  nullable: true
  cluster: company
- name: user_type
  data_type: string
  description: 联系人类型
  nullable: true
  cluster: account
  dictionary: cust_person_info_user_type
- name: face_status
  data_type: string
  description: 人脸认证结果
  nullable: true
  cluster: certification
  dictionary: cust_person_info_face_status
- name: auth_application
  data_type: string
  description: 开通产品
  nullable: true
  cluster: account
- name: realname_status
  data_type: string
  description: 实名认证
  nullable: true
  cluster: certification
  dictionary: cust_person_info_realname_status
- name: platform_user_id
  data_type: number
  description: 运营系统用户id
  nullable: true
  cluster: account
- name: en_name
  data_type: string
  description: 姓名(英文)
  nullable: true
  cluster: profile
- name: birth_date
  data_type: temporal
  description: 出生日期
  nullable: true
  cluster: profile
- name: en_name_end
  data_type: string
  description: 人名 (英文)
  nullable: true
  cluster: profile
- name: test_data
  data_type: string
  description: ''
  nullable: true
  cluster: misc
- name: company_type
  data_type: string
  description: ''
  nullable: true
  cluster: company
  dictionary: cust_person_info_company_type
- name: operator
  data_type: string
  description: ''
  nullable: true
  cluster: operator
- name: handby_person
  data_type: string
  description: ''
  nullable: true
  cluster: handler
- name: operator_id
  data_type: string
  description: 运营人id
  nullable: true
  cluster: operator
- name: operator_realname
  data_type: string
  description: 运营人姓名
  nullable: true
  cluster: operator
- name: phone_realname_status
  data_type: string
  description: 手机实名状态
  nullable: true
  cluster: certification
- name: handby_person_name
  data_type: string
  description: 建档经办人名字
  nullable: true
  cluster: handler
- name: user_name
  data_type: string
  description: 登录账号
  nullable: true
  cluster: account
- name: cust_build_status
  data_type: string
  description: 建档状态
  nullable: true
  cluster: company
  dictionary: cust_person_info_cust_build_status
- name: operator_push_system
  data_type: string
  description: 经办人推送系统列表
  nullable: true
  cluster: operator
  dictionary: cust_person_info_operator_push_system
- name: skip_auth_flag
  data_type: string
  description: 跳过实名认证标识
  nullable: true
  cluster: certification
  dictionary: cust_person_info_skip_auth_flag
- name: source
  data_type: string
  description: 来源
  nullable: true
  cluster: account
  dictionary: cust_person_info_source
- name: ext_data
  data_type: string
  description: 扩展字段
  nullable: true
  cluster: misc
- name: real_name_result
  data_type: string
  description: 实名认证结果
  nullable: true
  cluster: certification
  dictionary: cust_person_info_real_name_result
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_person_info.ref_cust_company_info
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.cust_company_id
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_person_info.cust_company_id
```
