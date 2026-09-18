---
type: table
title: 客户变更记录
page_key: cust_change_record
belong: tables
status: draft
anchors: [cust_change_record]
sources: ['database_schema:lowcode_pplatform.cust_change_record']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_change_cfg, cust_change_record__alter_mode, cust_change_record__admin_auth,
  cust_change_record__legal_auth, cust_change_record__cust_type, cust_change_record__status,
  cust_change_record__enable, cust_change_record__cust_company_type, cust_change_record__msg_send,
  cust_change_record__need_cust_confirm, cust_change_record__need_resign_auth, cust_change_record__oper_channel,
  cust_change_record__electronic_auth_sign_status]
---

# 客户变更记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_change_record
database: lowcode_pplatform
desc: 客户变更记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_name]
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
  dict: ['1', '2']
  label: [平台变更, 企业自行变更]
- name: admin_auth
  type: string
  desc: 企业管理授权
  dict: [N, Y]
- name: legal_auth
  type: string
  desc: 法人代表授权
  dict: [N, Y]
- name: alter_type
  type: string
  desc: 变更类型
- name: cust_type
  type: string
  desc: 客户类型
  dict: ['2', '1', '4', '3']
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
  dict: [CUST_CHECK_PASS, CUST_CHECK_REJECT, CUST_CHECK_CHECKING, '1', CUST_CHECK_BACKTOCUSTOM,
    'returnCust-2026-07-03 10:24', 'returnCust-2026-07-15 17:30', 'returnCust-2026-07-22
      14:55', CUSTS003, 'returnCust-2024-07-17 10:10', 'returnCust-2024-09-10 14:10',
    'returnCust-2024-11-01 14:16', 'returnCust-2024-11-05 10:03', 'returnCust-2024-11-12
      10:05', 'returnCust-2025-01-17 14:38', 'returnCust-2025-07-22 12:03', 'returnCust-2026-05-25
      14:55', 'returnCust-2026-05-22 20:22']
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
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
  dict: [SUPPLIER, CORE, FINANCE, PROJECT_COMPANY, CORPORATION_COMPANY, PLATFORM_OPERATOR_COMPANY,
    '["CORE","SUPPLIER"]', '["CORE"]', '["SUPPLIER"]', '["SUPPLIER","CORE"]', DEALER,
    CORE_MANAGER]
- name: alter_type_id
  type: string
  desc: 变更项记录id
- name: msg_send
  type: string
  desc: 消息发送
  dict: [Y, N]
- name: need_cust_confirm
  type: string
  desc: 是否需要客户确认
  dict: [Y, N]
- name: need_resign_auth
  type: string
  desc: 是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读
  dict: [Y, N]
  label: [是, 否]
- name: oper_channel
  type: string
  desc: 运营中台变更渠道
  dict: [operation-pplatform-common-new, operation-pplatform-not-edit-new, DIRECT_INIT]
- name: electronic_auth_sign_status
  type: string
  dict: [VOIDED, SIGNED, PENDING]
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
