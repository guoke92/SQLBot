---
type: table
title: CA服务费企业主数据
page_key: ca_fee_company
belong: tables
status: draft
anchors:
- ca_fee_company
sources:
- database_schema:lowcode_pplatform.ca_fee_company
- code_path:CaFeeCompanyBizMapper.java:13
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- ca_fee_order
- ca_fee_special_config
- cust_company_info
- tenant_project
- tenant_setting_config
- ca_fee_company__fee_locked
- ca_fee_company__pay_status
- ca_fee_company__source_company_type
- ca_fee_company__renew_remind_sent
- ca_fee_company__special_config_flag
- ca_fee_company__ca_status
- ca_fee_company__enable
---
# CA服务费企业主数据

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: ca_fee_company
database: lowcode_pplatform
desc: CA服务费企业主数据
inactive: false
primary_key:
- id
grain: 一统码一行企业宽表，按 certification_no 唯一
name_anchors:
- company_name
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: certification_no
  type: string
  desc: 统一社会信用代码
- name: company_name
  type: string
  desc: 企业名称
- name: tenant_id
  type: number
  desc: 首次锁定来源租户
- name: locked_annual_fee
  type: number
  desc: 首次缴费成功后锁定的年费标准（元）
- name: fee_locked
  type: string
  desc: 是否已锁定年费标准
  dict:
  - N
  - Y
  label:
    N: 否
    Y: 是
- name: pay_status
  type: string
  desc: 缴费状态：PAID 已缴费 / UNPAID 未缴费
  dict:
  - UNPAID
  - PAID
  label:
  - 未缴费
  - 已缴费
  written_with:
  - service_start
  - service_end
- name: service_start
  type: temporal
  desc: 当前 CA 服务费服务周期起始日（含）
  written_with:
  - pay_status
  - service_end
- name: service_end
  type: temporal
  desc: 当前 CA 服务费服务周期截止日（含）
  written_with:
  - pay_status
  - service_start
- name: source_project_id
  type: number
  desc: 首次锁定来源项目 ID
- name: source_company_type
  type: string
  desc: 首次锁定来源企业角色，如 SUPPLIER/CORE
  dict:
  - SUPPLIER
  - CORE
  - PROJECT_COMPANY
  label:
    SUPPLIER: 供应商
    CORE: 核心企业
- name: renew_remind_sent
  type: string
  desc: 本期续费待办是否已生成：Y 已生成 / N 未生成
  dict:
  - N
  - Y
  label:
    N: 未生成
    Y: 已生成
- name: special_config_flag
  type: string
  desc: 是否存在生效中的特殊配置快照
  dict:
  - N
  - Y
  label:
  - 否
  - 是
- name: special_annual_fee
  type: number
  desc: 特殊配置后应缴年费（元）
- name: ca_status
  type: string
  desc: CA签章状态
  dict:
  - NORMAL
  - CANCELLED
  - UNKNOWN
  - EXPIRED
  - UNREGISTERED
  label:
  - 有效
  - 已注销
  - 未注册
  - 已过期
  - 未注册
- name: ext_json
  type: string
  desc: 扩展字段 JSON预留
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
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
default_filter:
  predicate: ca_fee_company.enable = 'Y'
  trust: confirmed
  evidence: code_path:CaFeeCompanyBizMapper.java:13
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_fee_company.certification_no
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:CaFeeCompanyCaStatusSupport.java:85
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: ca_fee_company.source_project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeOrderService.java:456
source: l1_code
join_role: identity
priority: primary
authenticity_note: 首次锁定年费时记下源项目。
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: ca_fee_company.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeOrderService.java:458
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_company.certification_no
right: ca_fee_order.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeOrderService.java:440
source: l1_code
join_role: identity
priority: primary
authenticity_note: 企业宽表与订单按统码关联。
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_company.source_project_id
right: ca_fee_order.project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep_cont:live_fk_like;code:copy same project
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: code:copy same project
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_company.certification_no
right: ca_fee_special_config.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_fk_like R→L=0.98
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: CA 特殊配置↔fee_company 统码
```

## 页面链接

### 关联表

- [[tables/ca_fee_order]]
- [[tables/ca_fee_special_config]]
- [[tables/cust_company_info]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]

### 概念

- [[concepts/ca_fee_company_pay_status]]
- [[concepts/ca_fee_paid]]
- [[concepts/ca_open_status]]
- [[concepts/certification_no_term]]

### 字典

- [[dicts/ca_fee_company__fee_locked]]（`ca_fee_company.fee_locked`）
- [[dicts/ca_fee_company__pay_status]]（`ca_fee_company.pay_status`）
- [[dicts/ca_fee_company__source_company_type]]（`ca_fee_company.source_company_type`）
- [[dicts/ca_fee_company__renew_remind_sent]]（`ca_fee_company.renew_remind_sent`）
- [[dicts/ca_fee_company__special_config_flag]]（`ca_fee_company.special_config_flag`）
- [[dicts/ca_fee_company__ca_status]]（`ca_fee_company.ca_status`）
- [[dicts/ca_fee_company__enable]]（`ca_fee_company.enable`）
