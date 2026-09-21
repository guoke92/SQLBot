---
type: table
title: 协议迁移记录
page_key: argeement_migratory_record
belong: tables
status: draft
anchors: [argeement_migratory_record]
sources: ['database_schema:lowcode_pplatform.argeement_migratory_record']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, argeement_migratory_record__platform_product_code, argeement_migratory_record__status,
  argeement_migratory_record__agreement_type, argeement_migratory_record__sign_mode,
  argeement_migratory_record__is_new, argeement_migratory_record__pull_num, argeement_migratory_record__enable]
---

# 协议迁移记录

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
desc: 协议迁移记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, agreement_name]
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
  desc: 产融客户id
- name: platform_product_code
  type: string
  desc: 产品编码
  dict: [ACFLOW, RVSFACTOR_PC, ORDER, AMS, BEECREDIT, STORAGE, VOUCHER]
- name: status
  type: number
  desc: 状态
  dict: ['1', '0']
- name: agreement_type
  type: string
  desc: 协议类型
  dict: [PrivacyPolicy, UserProtocol, CustPersonLicense, CFCA_Auth, ProductProtocolAcflow,
    ProductProtocolRvsfactor_PC, ProductProtocolOrder, ProductProtocolAms, BS_Auth,
    ProductProtocolBeecredit, ProductProtocolStorage, ProductProtocolVoucher]
- name: agreement_path
  type: string
  desc: 协议路径
- name: agreement_name
  type: string
  desc: 协议名称
- name: agreement_no
  type: string
  desc: 协议编号
- name: effect_date
  type: temporal
  desc: 协议生效日
- name: sign_mode
  type: string
  desc: 签署模式
  dict: ['02', '01', '03']
- name: expire_date
  type: temporal
  desc: 失效时间
- name: is_new
  type: string
  desc: 是否新数据
  dict: ['yes', 'no']
- name: pull_num
  type: number
  desc: 拉取次数
  dict: ['0', '20', '1', '3', '2', '21', '4', '24', '22', '5', '28', '27', '14', '8',
    '23', '10', '33', '25', '31', '29', '17', '11', '7', '13', '55', '51']
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
- name: sign_date
  type: temporal
  desc: 签署日期
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: argeement_migratory_record.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.argeement_migratory_record.platform_product_code;database_profile:lowcode_pplatform.argeement_migratory_record.platform_product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 2
  miss: 2
  deepened: false
  query_ok: true
  authenticity: unknown
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/argeement_migratory_record__platform_product_code]]（`argeement_migratory_record.platform_product_code`）
- [[dicts/argeement_migratory_record__status]]（`argeement_migratory_record.status`）
- [[dicts/argeement_migratory_record__agreement_type]]（`argeement_migratory_record.agreement_type`）
- [[dicts/argeement_migratory_record__sign_mode]]（`argeement_migratory_record.sign_mode`）
- [[dicts/argeement_migratory_record__is_new]]（`argeement_migratory_record.is_new`）
- [[dicts/argeement_migratory_record__pull_num]]（`argeement_migratory_record.pull_num`）
- [[dicts/argeement_migratory_record__enable]]（`argeement_migratory_record.enable`）
