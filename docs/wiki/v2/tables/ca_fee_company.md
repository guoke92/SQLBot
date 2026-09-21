---
type: table
title: CA服务费企业主数据
page_key: ca_fee_company
belong: tables
status: draft
anchors: [ca_fee_company]
sources: ['database_schema:lowcode_pplatform.ca_fee_company']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_order, ca_fee_company__locked_annual_fee, ca_fee_company__fee_locked,
  ca_fee_company__pay_status, ca_fee_company__source_company_type, ca_fee_company__renew_remind_sent,
  ca_fee_company__special_config_flag, ca_fee_company__special_annual_fee, ca_fee_company__ca_status,
  ca_fee_company__enable]
---

# CA服务费企业主数据

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: ca_fee_company
database: lowcode_pplatform
desc: CA服务费企业主数据
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [company_name, code, name]
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
  dict: ['100', '80', '60', '88', '200', '90', '13', '70', '16', '10', '12', '50',
    '0', '125', '190', '170', '160', '140', '180']
- name: fee_locked
  type: string
  desc: 是否已锁定年费标准
  dict: [N, Y]
- name: pay_status
  type: string
  desc: 缴费状态：PAID 已缴费 / UNPAID 未缴费
  dict: [UNPAID, PAID]
  label: [未缴费, 已缴费]
- name: service_start
  type: temporal
  desc: 当前 CA 服务费服务周期起始日（含）
- name: service_end
  type: temporal
  desc: 当前 CA 服务费服务周期截止日（含）
- name: source_project_id
  type: number
  desc: 首次锁定来源项目 ID
- name: source_company_type
  type: string
  desc: 首次锁定来源企业角色，如 SUPPLIER/CORE
  dict: [SUPPLIER, CORE, PROJECT_COMPANY]
- name: renew_remind_sent
  type: string
  desc: 本期续费待办是否已生成：Y 已生成 / N 未生成
  dict: [N, Y]
  label: [未生成, 已生成]
- name: special_config_flag
  type: string
  desc: 是否存在生效中的特殊配置快照
  dict: [N, Y]
- name: special_annual_fee
  type: number
  desc: 特殊配置后应缴年费（元）
  dict: ['100', '0', '200', '12', '33', '16', '190', '170', '160', '140', '180', '80',
    '13', '70', '10']
- name: ca_status
  type: string
  desc: CA签章状态
  dict: [NORMAL, CANCELLED, UNKNOWN]
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

## 页面链接

### 关联表

- [[tables/ca_fee_order]]

### 字典

- [[dicts/ca_fee_company__locked_annual_fee]]（`ca_fee_company.locked_annual_fee`）
- [[dicts/ca_fee_company__fee_locked]]（`ca_fee_company.fee_locked`）
- [[dicts/ca_fee_company__pay_status]]（`ca_fee_company.pay_status`）
- [[dicts/ca_fee_company__source_company_type]]（`ca_fee_company.source_company_type`）
- [[dicts/ca_fee_company__renew_remind_sent]]（`ca_fee_company.renew_remind_sent`）
- [[dicts/ca_fee_company__special_config_flag]]（`ca_fee_company.special_config_flag`）
- [[dicts/ca_fee_company__special_annual_fee]]（`ca_fee_company.special_annual_fee`）
- [[dicts/ca_fee_company__ca_status]]（`ca_fee_company.ca_status`）
- [[dicts/ca_fee_company__enable]]（`ca_fee_company.enable`）
