---
type: table
title: 租户项目审批备注信息
page_key: tenant_project_approval_flow_comment
belong: tables
status: draft
anchors: [tenant_project_approval_flow_comment]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_comment']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow_file, tenant_project_approval_flow_comment__ref_tenant_project_approval_flow_comment_approval,
  tenant_project_approval_flow_comment__enable]
---

# 租户项目审批备注信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_comment
database: lowcode_pplatform
desc: 租户项目审批备注信息
inactive: false
primary_key: [id]
grain: 审批备注；apaas 有 @TableName DO，业务侧少直接引用
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: content
  type: string
  desc: 备注内容
- name: cc_user_id
  type: string
  desc: 抄送相关人员
- name: ref_tenant_project_approval_flow_comment_approval
  type: string
  desc: 关联项目审批
  dict: [23099f85ba3e478b95eeba5b4262de36, 0b913987d10e416c83bbc4810153db74, 049c5778d6384fa783a2acef5d70ce25,
    38acfe09cd0e40bda24670a8a28c0979, 61812482bc4e4a07b58e5d4f630d0987, edd9c1a030f4438ebdcd6956cfbfaa28,
    d96fcb4cb3284bacbafcfba37aa9d3e8, 91ed68bc0b8049e6b89a7a969b96265a, c9ebf8c5d2c244cfbb6c7888243e37c1,
    842d002e23e444889f0c5a634091199e, 400f36ce6321401ab2d5c674d6eb7761, d18f2f09df29422981fb3e2f024dfabe,
    25521e84d17b443e84aec5aeb0dbe4e3, d397456052f446f3aa6251077dbd3746, bad5b6f122e54a91a364dc98adb3f685,
    2f42c8f8b89a42d38021dca2adf775a1, 71864a5c417f42189751e94d0f3354d7, 1bce949920f044cab288db282a2d3319,
    f54697663e6b470098a13666989ac1aa, a408164d32534544bafa0f5d5c94761a, a1798bd113d541e891a42adcf2cd4522,
    ffa673eec1184c9b89ab8abac1d56d49]
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y]
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
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_comment_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 22
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_file]]

### 字典

- [[dicts/tenant_project_approval_flow_comment__ref_tenant_project_approval_flow_comment_approval]]（`tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval`）
- [[dicts/tenant_project_approval_flow_comment__enable]]（`tenant_project_approval_flow_comment.enable`）
