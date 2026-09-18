---
type: table
title: CA服务费订单
page_key: ca_fee_order
belong: tables
status: draft
anchors: [ca_fee_order]
sources: ['database_schema:lowcode_pplatform.ca_fee_order']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_company, ca_fee_project_config, ca_fee_order__company_type, ca_fee_order__order_type,
  ca_fee_order__order_status, ca_fee_order__pay_method, ca_fee_order__bocom_txn_sts,
  ca_fee_order__agreement_signed, ca_fee_order__invoice_status, ca_fee_order__enable]
---

# CA服务费订单

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `tenant_id`, `operate_logs`, `version`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### order

`order_no`, `order_type`, `order_status`, `close_reason`

### company

`company_id`, `certification_no`, `company_name`, `company_type`, `organization_id`

### project

`project_id`, `project_name`

### payment

`annual_fee`, `pay_amount`, `pay_method`, `pay_remark`, `pay_time`

### bocom

`bocom_plfm_ser_no`, `bocom_plfm_bsn_id`, `bocom_req_sn`, `bocom_txn_sts`, `bocom_pay_info`

### service

`service_start`, `service_end`

### agreement

`agreement_version`, `agreement_signed`, `agreement_sign_time`, `agreement_file_path`

### invoice

`invoice_status`, `invoice_no`, `invoice_file_path`, `invoice_request_id`, `invoice_fail_reason`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: ca_fee_order
database: lowcode_pplatform
description: CA服务费订单
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [company_name, project_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: order
  title: 订单属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: company
  title: 企业与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: project
  title: 项目
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: payment
  title: 费用与支付
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: bocom
  title: 交e保对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: service
  title: 服务周期
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: agreement
  title: 收费协议
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: invoice
  title: 发票
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: order_no
  data_type: string
  description: 订单号，唯一键
  cluster: order
- name: company_id
  data_type: number
  description: 企业 ID
  cluster: company
- name: certification_no
  data_type: string
  description: 统一社会信用代码
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  cluster: company
- name: project_id
  data_type: number
  description: 触发项目 ID
  cluster: project
- name: project_name
  data_type: string
  description: 项目名称
  cluster: project
- name: tenant_id
  data_type: number
  description: 所属租户 ID
  cluster: common
- name: company_type
  data_type: string
  description: 企业角色：SUPPLIER/CORE
  cluster: company
  dictionary: ca_fee_order__company_type
- name: order_type
  data_type: string
  description: 订单类型
  cluster: order
  dictionary: ca_fee_order__order_type
- name: order_status
  data_type: string
  description: 订单状态
  cluster: order
  dictionary: ca_fee_order__order_status
- name: annual_fee
  data_type: number
  description: 应缴年费（元）
  cluster: payment
- name: pay_amount
  data_type: number
  description: 实缴金额（元）
  cluster: payment
- name: pay_method
  data_type: string
  description: 支付方式
  cluster: payment
  dictionary: ca_fee_order__pay_method
- name: pay_remark
  data_type: string
  description: 打款备注
  cluster: payment
- name: pay_time
  data_type: temporal
  description: 缴费成功时间
  cluster: payment
- name: bocom_plfm_ser_no
  data_type: string
  description: 交e保平台流水号
  cluster: bocom
- name: bocom_plfm_bsn_id
  data_type: string
  description: 平台业务编号
  cluster: bocom
- name: bocom_req_sn
  data_type: string
  description: 请求流水号
  cluster: bocom
- name: bocom_txn_sts
  data_type: string
  description: 响应状态
  cluster: bocom
  dictionary: ca_fee_order__bocom_txn_sts
- name: service_start
  data_type: temporal
  description: 本单服务周期起始日（含）
  cluster: service
- name: service_end
  data_type: temporal
  description: 本单服务周期截止日（含）
  cluster: service
- name: agreement_version
  data_type: string
  description: 签署时绑定的收费协议版本号
  cluster: agreement
- name: agreement_signed
  data_type: string
  description: 是否已签署收费协议
  cluster: agreement
  dictionary: ca_fee_order__agreement_signed
- name: agreement_sign_time
  data_type: temporal
  description: 收费协议签署时间
  cluster: agreement
- name: agreement_file_path
  data_type: string
  description: 签章后协议文件 COS 路径
  cluster: agreement
- name: bocom_pay_info
  data_type: string
  description: 交e保虚拟户快照JSON
  cluster: bocom
- name: invoice_status
  data_type: string
  description: 发票状态
  cluster: invoice
  dictionary: ca_fee_order__invoice_status
- name: invoice_no
  data_type: string
  description: 发票号码
  cluster: invoice
- name: invoice_file_path
  data_type: string
  description: 发票PDF 文件COS路径
  cluster: invoice
- name: invoice_request_id
  data_type: string
  description: 开票平台请求号
  cluster: invoice
- name: invoice_fail_reason
  data_type: string
  description: 开票失败原因
  cluster: invoice
- name: operate_logs
  data_type: string
  description: 操作轨迹 JSON 数组
  cluster: common
- name: close_reason
  data_type: string
  description: 关闭原因（关开关/手动关闭等）
  cluster: order
- name: version
  data_type: number
  description: 乐观锁版本号，更新订单状态时自增
  cluster: common
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: ca_fee_order__enable
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
  cluster: approval
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
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: company
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: ca_fee_company.id
right: ca_fee_order.company_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.ca_fee_order.company_id;database_profile:lowcode_pplatform.ca_fee_order.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业 ID
overlap:
  probed: true
  ratio: 0.0
  sample_size: 145
  miss: 145
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名/注释有 company 语义关联（企业 ID），但实测 overlap 0.0（145/145 未命中），值域不契合，不能判
  likely
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_project_config.id
right: ca_fee_order.project_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.ca_fee_order.project_id
source: llm
join_role: identity
priority: primary
name_evidence:
  match: llm_propose
  stem: project_id
  comment: 注释语义对应（项目配置主键 ← 触发项目 ID），作为该列唯一合理的父表 id 边保留待验；overlap 采样仅 10 且为 0.0，需人工复核
overlap:
  probed: true
  ratio: 0.0
  sample_size: 10
  authenticity: unlikely
authenticity_note: 注释语义对应（项目配置主键 ← 触发项目 ID），作为该列唯一合理的父表 id 边保留待验；overlap 采样仅 10 且为
  0.0，需人工复核
```

## 页面链接

### 关联表

- [[tables/ca_fee_company]]
- [[tables/ca_fee_project_config]]

### 字典

- [[dicts/ca_fee_order__company_type]]（`ca_fee_order.company_type`）
- [[dicts/ca_fee_order__order_type]]（`ca_fee_order.order_type`）
- [[dicts/ca_fee_order__order_status]]（`ca_fee_order.order_status`）
- [[dicts/ca_fee_order__pay_method]]（`ca_fee_order.pay_method`）
- [[dicts/ca_fee_order__bocom_txn_sts]]（`ca_fee_order.bocom_txn_sts`）
- [[dicts/ca_fee_order__agreement_signed]]（`ca_fee_order.agreement_signed`）
- [[dicts/ca_fee_order__invoice_status]]（`ca_fee_order.invoice_status`）
- [[dicts/ca_fee_order__enable]]（`ca_fee_order.enable`）
