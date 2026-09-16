---
type: table
title: CA服务费订单
page_key: ca_fee_order
belong: tables
status: draft
aliases: []
anchors:
- ca_fee_order
sources:
- database_schema:lowcode_pplatform.ca_fee_order
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# CA服务费订单

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `operate_logs`, `version`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### order

`order_no`, `order_type`, `order_status`, `close_reason`

### payment

`annual_fee`, `pay_amount`, `pay_method`, `pay_remark`, `pay_time`

### company

`company_id`, `certification_no`, `company_name`, `company_type`, `organization_id`

### project

`project_id`, `project_name`

### bocom

`bocom_plfm_ser_no`, `bocom_plfm_bsn_id`, `bocom_req_sn`, `bocom_txn_sts`, `bocom_pay_info`

### service

`service_start`, `service_end`

### agreement

`agreement_version`, `agreement_signed`, `agreement_sign_time`, `agreement_file_path`

### invoice

`invoice_status`, `invoice_no`, `invoice_file_path`, `invoice_request_id`, `invoice_fail_reason`

### tenant

`tenant_id`, `app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: ca_fee_order
database: lowcode_pplatform
description: CA服务费订单
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- company_name
- project_name
- code
- name
clusters:
- key: common
  title: 通用与审计字段
  include: always
- key: order
  title: 订单与生命周期
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: payment
  title: 缴费与金额
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: company
  title: 企业主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: project
  title: 触发项目
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: bocom
  title: 交e保银行侧交互
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: service
  title: 服务周期
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: agreement
  title: 收费协议
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: invoice
  title: 发票
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_order
- key: approval
  title: 审批流程
  confidence: proposed
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
  nullable: true
  cluster: order
- name: company_id
  data_type: number
  description: 企业 ID
  nullable: true
  cluster: company
- name: certification_no
  data_type: string
  description: 统一社会信用代码
  nullable: true
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: company
- name: project_id
  data_type: number
  description: 触发项目 ID
  nullable: true
  cluster: project
- name: project_name
  data_type: string
  description: 项目名称
  nullable: true
  cluster: project
- name: tenant_id
  data_type: number
  description: 所属租户 ID
  nullable: true
  cluster: tenant
- name: company_type
  data_type: string
  description: 企业角色：SUPPLIER/CORE
  nullable: true
  cluster: company
  dictionary: ca_fee_order_company_type
- name: order_type
  data_type: string
  description: 订单类型
  nullable: true
  cluster: order
  dictionary: ca_fee_order_order_type
- name: order_status
  data_type: string
  description: 订单状态
  nullable: true
  cluster: order
  dictionary: ca_fee_order_order_status
- name: annual_fee
  data_type: number
  description: 应缴年费（元）
  nullable: true
  cluster: payment
- name: pay_amount
  data_type: number
  description: 实缴金额（元）
  nullable: true
  cluster: payment
- name: pay_method
  data_type: string
  description: 支付方式
  nullable: true
  cluster: payment
- name: pay_remark
  data_type: string
  description: 打款备注
  nullable: true
  cluster: payment
- name: pay_time
  data_type: temporal
  description: 缴费成功时间
  nullable: true
  cluster: payment
- name: bocom_plfm_ser_no
  data_type: string
  description: 交e保平台流水号
  nullable: true
  cluster: bocom
- name: bocom_plfm_bsn_id
  data_type: string
  description: 平台业务编号
  nullable: true
  cluster: bocom
- name: bocom_req_sn
  data_type: string
  description: 请求流水号
  nullable: true
  cluster: bocom
- name: bocom_txn_sts
  data_type: string
  description: 响应状态
  nullable: true
  cluster: bocom
- name: service_start
  data_type: temporal
  description: 本单服务周期起始日（含）
  nullable: true
  cluster: service
- name: service_end
  data_type: temporal
  description: 本单服务周期截止日（含）
  nullable: true
  cluster: service
- name: agreement_version
  data_type: string
  description: 签署时绑定的收费协议版本号
  nullable: true
  cluster: agreement
- name: agreement_signed
  data_type: string
  description: 是否已签署收费协议
  nullable: true
  cluster: agreement
  dictionary: ca_fee_order_agreement_signed
- name: agreement_sign_time
  data_type: temporal
  description: 收费协议签署时间
  nullable: true
  cluster: agreement
- name: agreement_file_path
  data_type: string
  description: 签章后协议文件 COS 路径
  nullable: true
  cluster: agreement
- name: bocom_pay_info
  data_type: string
  description: 交e保虚拟户快照JSON
  nullable: true
  cluster: bocom
- name: invoice_status
  data_type: string
  description: 发票状态
  nullable: true
  cluster: invoice
  dictionary: ca_fee_order_invoice_status
- name: invoice_no
  data_type: string
  description: 发票号码
  nullable: true
  cluster: invoice
- name: invoice_file_path
  data_type: string
  description: 发票PDF 文件COS路径
  nullable: true
  cluster: invoice
- name: invoice_request_id
  data_type: string
  description: 开票平台请求号
  nullable: true
  cluster: invoice
- name: invoice_fail_reason
  data_type: string
  description: 开票失败原因
  nullable: true
  cluster: invoice
- name: operate_logs
  data_type: string
  description: 操作轨迹 JSON 数组
  nullable: true
  cluster: common
- name: close_reason
  data_type: string
  description: 关闭原因（关开关/手动关闭等）
  nullable: true
  cluster: order
- name: version
  data_type: number
  description: 乐观锁版本号，更新订单状态时自增
  nullable: true
  cluster: common
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: ca_fee_order_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: company
```
