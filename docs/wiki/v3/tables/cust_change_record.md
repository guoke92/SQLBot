---
type: table
title: 客户变更记录
page_key: cust_change_record
belong: tables
status: draft
anchors:
- cust_change_record
sources:
- database_schema:lowcode_pplatform.cust_change_record
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_change_cfg
- cust_company_info
- cust_change_record__enable
- cust_change_record__need_cust_confirm
- cust_change_record__need_resign_auth
- cust_change_record__electronic_auth_sign_status
---
# 客户变更记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_change_record
database: lowcode_pplatform
desc: 客户变更记录
inactive: false
primary_key:
- id
grain: 企业变更单；直推单 oper_channel=DIRECT_INIT + serial_no 幂等
name_anchors:
- code
- name
- cust_name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: cust_id
  type: number
  desc: 客户记录id
- name: cust_name
  type: string
  desc: 客户名称
- name: alter_data
  type: string
  desc: 变更数据
- name: alter_mode
  type: string
  desc: 变更方式
- name: admin_auth
  type: string
  desc: 企业管理授权
- name: legal_auth
  type: string
  desc: 法人代表授权
- name: alter_type
  type: string
  desc: 变更类型
- name: cust_type
  type: string
  desc: 客户类型
- name: oper_app_no
  type: string
  desc: 运营中台流程编号
- name: oper_cust_info
  type: string
  desc: 运营中台客户信息
- name: pp_cust_info
  type: string
  desc: 产融客户信息
- name: status
  type: string
  desc: 变更状态
  written_with:
  - need_resign_auth
  - need_cust_confirm
  - electronic_auth_sign_status
  - oper_channel
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: oper_cust_id
  type: number
  desc: 运营中台客户id
- name: cust_company_type
  type: string
  desc: 客户企业类型
- name: alter_type_id
  type: string
  desc: 变更项记录id
- name: msg_send
  type: string
  desc: 消息发送
- name: need_cust_confirm
  type: string
  desc: 是否需要客户确认
  dict:
  - Y
  - N
  written_with:
  - need_resign_auth
  - electronic_auth_sign_status
  - status
  - oper_channel
  label:
    Y: 是
    N: 否
- name: need_resign_auth
  type: string
  desc: 是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读
  dict:
  - Y
  - N
  label:
    Y: 是
    N: 否
  written_with:
  - need_cust_confirm
  - electronic_auth_sign_status
  - status
  - oper_channel
- name: oper_channel
  type: string
  desc: 运营中台变更渠道
  written_with:
  - need_resign_auth
  - need_cust_confirm
  - electronic_auth_sign_status
  - status
- name: electronic_auth_sign_status
  type: string
  dict:
  - VOIDED
  - SIGNED
  - PENDING
  - UPLOAD_FAILED
  - FAILED
  label:
  - 作废
  - 已签署
  - 待签署
  - 影像上传失败
  - 签署失败
  written_with:
  - need_resign_auth
  - need_cust_confirm
  - status
  - oper_channel
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_change_record.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperCustFacade.java:1417
source: l1_code
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
authenticity_note: 变更记录 cust_id 是企业主键。
```
```ground:relation
type: EQUI_JOIN
left: cust_change_cfg.id
right: cust_change_record.alter_type_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_shared_domain
source: full_sweep
join_role: identity
priority: primary
authenticity_note: code+live
```

## 页面链接

### 关联表

- [[tables/cust_change_cfg]]
- [[tables/cust_company_info]]

### 概念

- [[concepts/alter_mode_self]]
- [[concepts/direct_init_change_record]]
- [[concepts/direct_init_need_resign]]
- [[concepts/electronic_auth_sign_status_term]]

### 字典

- [[dicts/cust_change_record__enable]]（`cust_change_record.enable`）
- [[dicts/cust_change_record__need_cust_confirm]]（`cust_change_record.need_cust_confirm`）
- [[dicts/cust_change_record__need_resign_auth]]（`cust_change_record.need_resign_auth`）
- [[dicts/cust_change_record__electronic_auth_sign_status]]（`cust_change_record.electronic_auth_sign_status`）
