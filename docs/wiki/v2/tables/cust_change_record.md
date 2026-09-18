---
type: table
title: 客户变更记录
page_key: cust_change_record
belong: tables
status: draft
anchors: [cust_change_record]
sources: ['database_schema:lowcode_pplatform.cust_change_record']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_change_cfg, cust_change_record__alter_mode, cust_change_record__admin_auth,
  cust_change_record__legal_auth, cust_change_record__cust_type, cust_change_record__status,
  cust_change_record__enable, cust_change_record__cust_company_type, cust_change_record__msg_send,
  cust_change_record__need_cust_confirm, cust_change_record__need_resign_auth, cust_change_record__oper_channel,
  cust_change_record__electronic_auth_sign_status]
---

# 客户变更记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### cust

`cust_id`, `cust_name`, `cust_type`, `cust_company_type`

### alter

`alter_data`, `alter_mode`, `alter_type`, `status`, `alter_type_id`

### oper

`oper_app_no`, `oper_cust_info`, `oper_cust_id`, `oper_channel`

### proc

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### auth

`admin_auth`, `legal_auth`, `need_resign_auth`, `electronic_auth_sign_status`

### notify

`msg_send`, `need_cust_confirm`

### other

`pp_cust_info`, `organization_id`

## 字段

```ground:table
table: cust_change_record
database: lowcode_pplatform
description: 客户变更记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_name]
clusters:
- key: common
  title: 通用
  include: always
- key: cust
  title: 客户信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: alter
  title: 变更内容
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: oper
  title: 运营中台
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: proc
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: auth
  title: 授权与签署
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: notify
  title: 确认与通知
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_change_record
- key: other
  title: 其他
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: cust_id
  data_type: number
  description: 客户记录id
  cluster: cust
- name: cust_name
  data_type: string
  description: 客户名称
  cluster: cust
- name: alter_data
  data_type: string
  description: 变更数据
  cluster: alter
- name: alter_mode
  data_type: string
  description: 变更方式
  cluster: alter
  dictionary: cust_change_record__alter_mode
- name: admin_auth
  data_type: string
  description: 企业管理授权
  cluster: auth
  dictionary: cust_change_record__admin_auth
- name: legal_auth
  data_type: string
  description: 法人代表授权
  cluster: auth
  dictionary: cust_change_record__legal_auth
- name: alter_type
  data_type: string
  description: 变更类型
  cluster: alter
- name: cust_type
  data_type: string
  description: 客户类型
  cluster: cust
  dictionary: cust_change_record__cust_type
- name: oper_app_no
  data_type: string
  description: 运营中台流程编号
  cluster: oper
- name: oper_cust_info
  data_type: string
  description: 运营中台客户信息
  cluster: oper
- name: pp_cust_info
  data_type: string
  description: 产融客户信息
  cluster: other
- name: status
  data_type: string
  description: 变更状态
  cluster: alter
  dictionary: cust_change_record__status
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_change_record__enable
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
  cluster: proc
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: proc
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: proc
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: proc
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: other
- name: oper_cust_id
  data_type: number
  description: 运营中台客户id
  cluster: oper
- name: cust_company_type
  data_type: string
  description: 客户企业类型
  cluster: cust
  dictionary: cust_change_record__cust_company_type
- name: alter_type_id
  data_type: string
  description: 变更项记录id
  cluster: alter
- name: msg_send
  data_type: string
  description: 消息发送
  cluster: notify
  dictionary: cust_change_record__msg_send
- name: need_cust_confirm
  data_type: string
  description: 是否需要客户确认
  cluster: notify
  dictionary: cust_change_record__need_cust_confirm
- name: need_resign_auth
  data_type: string
  description: 是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读
  cluster: auth
  dictionary: cust_change_record__need_resign_auth
- name: oper_channel
  data_type: string
  description: 运营中台变更渠道
  cluster: oper
  dictionary: cust_change_record__oper_channel
- name: electronic_auth_sign_status
  data_type: string
  cluster: auth
  dictionary: cust_change_record__electronic_auth_sign_status
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_change_record.cust_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_change_record.cust_id;database_profile:lowcode_pplatform.cust_change_record.cust_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 客户记录id
overlap:
  probed: true
  ratio: 0.9683
  ratio_reverse: 0.315
  sample_size: 284
  miss: 9
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: cust_id 注释「客户记录id」与客户主表 cust_company_info.id 语义一致，值域重叠 96.83%（反向
  31.5%，miss 9，sample 284），列名族同为 cust，判为 likely。
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_change_cfg.id
right: cust_change_record.alter_type_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_change_record.alter_type_id
source: llm
join_role: identity
priority: primary
name_evidence:
  match: llm_propose
  stem: alter_type_id
  comment: alter_type_id 注释「变更项记录id」，与 cust_change_cfg（客户变更配置）语义关联，值域部分契合（正向 0.6707，反向
    1.0，
overlap:
  probed: true
  ratio: 0.6707
  ratio_reverse: 1.0
  sample_size: 82
  authenticity: unknown
authenticity_note: alter_type_id 注释「变更项记录id」，与 cust_change_cfg（客户变更配置）语义关联，值域部分契合（正向
  0.6707，反向 1.0，sample 82），判为指向变更配置记录的可接受边，建议人工复核完整率。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_change_cfg]]

### 字典

- [[dicts/cust_change_record__alter_mode]]（`cust_change_record.alter_mode`）
- [[dicts/cust_change_record__admin_auth]]（`cust_change_record.admin_auth`）
- [[dicts/cust_change_record__legal_auth]]（`cust_change_record.legal_auth`）
- [[dicts/cust_change_record__cust_type]]（`cust_change_record.cust_type`）
- [[dicts/cust_change_record__status]]（`cust_change_record.status`）
- [[dicts/cust_change_record__enable]]（`cust_change_record.enable`）
- [[dicts/cust_change_record__cust_company_type]]（`cust_change_record.cust_company_type`）
- [[dicts/cust_change_record__msg_send]]（`cust_change_record.msg_send`）
- [[dicts/cust_change_record__need_cust_confirm]]（`cust_change_record.need_cust_confirm`）
- [[dicts/cust_change_record__need_resign_auth]]（`cust_change_record.need_resign_auth`）
- [[dicts/cust_change_record__oper_channel]]（`cust_change_record.oper_channel`）
- [[dicts/cust_change_record__electronic_auth_sign_status]]（`cust_change_record.electronic_auth_sign_status`）
