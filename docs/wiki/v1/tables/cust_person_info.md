---
type: table
title: 客户联系人表
page_key: cust_person_info
belong: tables
status: draft
anchors: [cust_person_info]
sources: ['database_schema:lowcode_pplatform.cust_person_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_build_record, cust_oper_change_record, cust_company_info, cust_person_info__enable,
  cust_person_info__app_tenant_code, cust_person_info__certification_type, cust_person_info__status,
  cust_person_info__user_type, cust_person_info__face_status, cust_person_info__realname_status,
  cust_person_info__test_data, cust_person_info__company_type, cust_person_info__cust_build_status,
  cust_person_info__operator_push_system, cust_person_info__skip_auth_flag, cust_person_info__source,
  cust_person_info__real_name_result]
---

# 客户联系人表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### act_procinst_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### identity

`name`, `phone`, `email`, `en_name`, `birth_date`, `en_name_end`

### certification_auth

`certification_type`, `certification_no`, `certification_expire`, `face_status`, `realname_status`, `phone_realname_status`, `skip_auth_flag`, `real_name_result`

### user_account

`user_id`, `status`, `user_type`, `platform_user_id`, `user_name`

### cust_company

`organization_id`, `main_data_id`, `ref_cust_company_info`, `cust_company_id`, `company_type`, `cust_build_status`

### operator_handby

`operator`, `handby_person`, `operator_id`, `operator_realname`, `handby_person_name`, `operator_push_system`

### misc

`auth_application`, `test_data`, `source`, `ext_data`

## 字段

```ground:table
table: cust_person_info
database: lowcode_pplatform
description: 客户联系人表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, en_name, handby_person_name, user_name]
clusters:
- key: common
  title: 通用
  include: always
- key: act_procinst_flow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: identity
  title: 联系人基本信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: certification_auth
  title: 证件与实名认证
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: user_account
  title: 用户账号
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: cust_company
  title: 客户企业关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: operator_handby
  title: 经办与运营
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_person_info
- key: misc
  title: 来源与扩展
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 姓名
  cluster: identity
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_person_info__enable
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
  cluster: act_procinst_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
  dictionary: cust_person_info__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: act_procinst_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: act_procinst_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: act_procinst_flow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: cust_company
- name: phone
  data_type: string
  description: 手机号
  cluster: identity
- name: certification_type
  data_type: string
  description: 证件类型
  cluster: certification_auth
  dictionary: cust_person_info__certification_type
- name: certification_no
  data_type: string
  description: 证件号码
  cluster: certification_auth
- name: certification_expire
  data_type: string
  description: 证件有效期
  cluster: certification_auth
- name: email
  data_type: string
  description: 邮箱
  cluster: identity
- name: user_id
  data_type: number
  description: 关联用户
  cluster: user_account
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: cust_company
- name: ref_cust_company_info
  data_type: string
  description: 关联企业
  cluster: cust_company
- name: status
  data_type: string
  description: 联系人账号状态
  cluster: user_account
  dictionary: cust_person_info__status
- name: cust_company_id
  data_type: number
  description: 冗余企业id
  cluster: cust_company
- name: user_type
  data_type: string
  description: 联系人类型
  cluster: user_account
  dictionary: cust_person_info__user_type
- name: face_status
  data_type: string
  description: 人脸认证结果
  cluster: certification_auth
  dictionary: cust_person_info__face_status
- name: auth_application
  data_type: string
  description: 开通产品
  cluster: misc
- name: realname_status
  data_type: string
  description: 实名认证
  cluster: certification_auth
  dictionary: cust_person_info__realname_status
- name: platform_user_id
  data_type: number
  description: 运营系统用户id
  cluster: user_account
- name: en_name
  data_type: string
  description: 姓名(英文)
  cluster: identity
- name: birth_date
  data_type: temporal
  description: 出生日期
  cluster: identity
- name: en_name_end
  data_type: string
  description: 人名 (英文)
  cluster: identity
- name: test_data
  data_type: string
  cluster: misc
  dictionary: cust_person_info__test_data
- name: company_type
  data_type: string
  cluster: cust_company
  dictionary: cust_person_info__company_type
- name: operator
  data_type: string
  cluster: operator_handby
- name: handby_person
  data_type: string
  cluster: operator_handby
- name: operator_id
  data_type: string
  description: 运营人id
  cluster: operator_handby
- name: operator_realname
  data_type: string
  description: 运营人姓名
  cluster: operator_handby
- name: phone_realname_status
  data_type: string
  description: 手机实名状态
  cluster: certification_auth
- name: handby_person_name
  data_type: string
  description: 建档经办人名字
  cluster: operator_handby
- name: user_name
  data_type: string
  description: 登录账号
  cluster: user_account
- name: cust_build_status
  data_type: string
  description: 建档状态
  cluster: cust_company
  dictionary: cust_person_info__cust_build_status
- name: operator_push_system
  data_type: string
  description: 经办人推送系统列表
  cluster: operator_handby
  dictionary: cust_person_info__operator_push_system
- name: skip_auth_flag
  data_type: string
  description: 跳过实名认证标识
  cluster: certification_auth
  dictionary: cust_person_info__skip_auth_flag
- name: source
  data_type: string
  description: 来源
  cluster: misc
  dictionary: cust_person_info__source
- name: ext_data
  data_type: string
  description: 扩展字段
  cluster: misc
- name: real_name_result
  data_type: string
  description: 实名认证结果
  cluster: certification_auth
  dictionary: cust_person_info__real_name_result
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.cust_company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_person_info.cust_company_id;database_profile:lowcode_pplatform.cust_person_info.cust_company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: stem_info
  stem: cust_company
  comment: 冗余企业id
overlap:
  probed: true
  ratio: 0.994
  sample_size: 166
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 对端 cust_company_info.id；注释「冗余企业id」，探测重叠率 0.994（sample 166，miss
  1），强支持为指向客户企业主表的外键边。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_person_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_person_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 关联企业
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 对端 cust_company_info.id；名称精确命中（关联企业）但探测重叠率 0.0（sample 200 全 miss），疑为历史/未启用字段，暂判
  unlikely。
```

## 页面链接

### 关联表

- [[tables/cust_build_record]]
- [[tables/cust_oper_change_record]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_person_info__enable]]（`cust_person_info.enable`）
- [[dicts/cust_person_info__app_tenant_code]]（`cust_person_info.app_tenant_code`）
- [[dicts/cust_person_info__certification_type]]（`cust_person_info.certification_type`）
- [[dicts/cust_person_info__status]]（`cust_person_info.status`）
- [[dicts/cust_person_info__user_type]]（`cust_person_info.user_type`）
- [[dicts/cust_person_info__face_status]]（`cust_person_info.face_status`）
- [[dicts/cust_person_info__realname_status]]（`cust_person_info.realname_status`）
- [[dicts/cust_person_info__test_data]]（`cust_person_info.test_data`）
- [[dicts/cust_person_info__company_type]]（`cust_person_info.company_type`）
- [[dicts/cust_person_info__cust_build_status]]（`cust_person_info.cust_build_status`）
- [[dicts/cust_person_info__operator_push_system]]（`cust_person_info.operator_push_system`）
- [[dicts/cust_person_info__skip_auth_flag]]（`cust_person_info.skip_auth_flag`）
- [[dicts/cust_person_info__source]]（`cust_person_info.source`）
- [[dicts/cust_person_info__real_name_result]]（`cust_person_info.real_name_result`）
