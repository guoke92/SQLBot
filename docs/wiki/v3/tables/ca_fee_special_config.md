---
type: table
title: CA服务费特殊企业配置
page_key: ca_fee_special_config
belong: tables
status: draft
anchors:
- ca_fee_special_config
sources:
- database_schema:lowcode_pplatform.ca_fee_special_config
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- ca_fee_company
- ca_fee_order
- cust_company_info
- tenant_project
- ca_fee_special_config__enable
---
# CA服务费特殊企业配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: ca_fee_special_config
database: lowcode_pplatform
desc: CA服务费特殊企业配置
inactive: false
primary_key:
- id
grain: catalog 有表；现网特殊企业写在 ca_fee_project_config.special_company_list JSON
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
- name: annual_fee
  type: number
  desc: 年费标准
- name: valid_start
  type: temporal
  desc: 有效期起
- name: valid_end
  type: temporal
  desc: 有效期止
- name: operate_logs
  type: string
  desc: 操作日志
- name: project_id
  type: number
  desc: 项目id
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
  label: [启用, 停用]
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
left: tenant_project.id
right: ca_fee_special_config.project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_fk_like R→L=1
source: orphan_repair
join_role: identity
priority: primary
authenticity_note: CA 特殊配置→项目
```
```ground:relation
type: EQUI_JOIN
left: ca_fee_order.project_id
right: ca_fee_special_config.project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_shared_domain B↔C
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: CA 场景附属↔订单同 project_id
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
```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_fee_special_config.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live R→L=0.93 certification hub
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 统码 hub
```

## 页面链接

### 关联表

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[tables/cust_company_info]]
- [[tables/tenant_project]]

### 概念

- [[concepts/certification_no_term]]

### 字典

- [[dicts/ca_fee_special_config__enable]]（`ca_fee_special_config.enable`）
