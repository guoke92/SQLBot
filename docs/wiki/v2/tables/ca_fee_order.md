---
type: table
title: CA服务费订单
page_key: ca_fee_order
belong: tables
status: draft
anchors: [ca_fee_order]
sources: ['database_schema:lowcode_pplatform.ca_fee_order']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_company, ca_fee_order__company_type, ca_fee_order__order_type, ca_fee_order__order_status,
  ca_fee_order__annual_fee, ca_fee_order__pay_amount, ca_fee_order__pay_method, ca_fee_order__bocom_plfm_bsn_id,
  ca_fee_order__bocom_txn_sts, ca_fee_order__agreement_version, ca_fee_order__agreement_signed,
  ca_fee_order__invoice_status, ca_fee_order__version, ca_fee_order__enable]
---

# CA服务费订单

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: ca_fee_order
database: lowcode_pplatform
desc: CA服务费订单
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [company_name, project_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: order_no
  type: string
  desc: 订单号，唯一键
- name: company_id
  type: number
  desc: 企业 ID
- name: certification_no
  type: string
  desc: 统一社会信用代码
- name: company_name
  type: string
  desc: 企业名称
- name: project_id
  type: number
  desc: 触发项目 ID
- name: project_name
  type: string
  desc: 项目名称
- name: tenant_id
  type: number
  desc: 所属租户 ID
- name: company_type
  type: string
  desc: 企业角色：SUPPLIER/CORE
  dict: [SUPPLIER, CORE, PROJECT_COMPANY]
- name: order_type
  type: string
  desc: 订单类型
  dict: [STOCK, FIRST, RENEW_EXPIRED, RENEW]
- name: order_status
  type: string
  desc: 订单状态
  dict: [CLOSED, PENDING, PAID, PAIDING, UNPAID]
- name: annual_fee
  type: number
  desc: 应缴年费（元）
  dict: ['100', '80', '60', '50', '0', '88', '120', '99', '90', '6', '160', '40',
    '16', '33', '156', '125', '70', '190', '170']
- name: pay_amount
  type: number
  desc: 实缴金额（元）
  dict: ['100', '80', '0', '60', '120', '6', '66', '99', '3', '50', '125', '90', '88']
- name: pay_method
  type: string
  desc: 支付方式
  dict: [BOCOM]
- name: pay_remark
  type: string
  desc: 打款备注
- name: pay_time
  type: temporal
  desc: 缴费成功时间
- name: bocom_plfm_ser_no
  type: string
  desc: 交e保平台流水号
- name: bocom_plfm_bsn_id
  type: string
  desc: 平台业务编号
  dict: ['31020250010']
- name: bocom_req_sn
  type: string
  desc: 请求流水号
- name: bocom_txn_sts
  type: string
  desc: 响应状态
  dict: ['00']
- name: service_start
  type: temporal
  desc: 本单服务周期起始日（含）
- name: service_end
  type: temporal
  desc: 本单服务周期截止日（含）
- name: agreement_version
  type: string
  desc: 签署时绑定的收费协议版本号
  dict: [V1.0]
- name: agreement_signed
  type: string
  desc: 是否已签署收费协议
  dict: [N, Y]
- name: agreement_sign_time
  type: temporal
  desc: 收费协议签署时间
- name: agreement_file_path
  type: string
  desc: 签章后协议文件 COS 路径
- name: bocom_pay_info
  type: string
  desc: 交e保虚拟户快照JSON
- name: invoice_status
  type: string
  desc: 发票状态
  dict: [PENDING, ISSUED]
- name: invoice_no
  type: string
  desc: 发票号码
- name: invoice_file_path
  type: string
  desc: 发票PDF 文件COS路径
- name: invoice_request_id
  type: string
  desc: 开票平台请求号
- name: invoice_fail_reason
  type: string
  desc: 开票失败原因
- name: operate_logs
  type: string
  desc: 操作轨迹 JSON 数组
- name: close_reason
  type: string
  desc: 关闭原因（关开关/手动关闭等）
- name: version
  type: number
  desc: 乐观锁版本号，更新订单状态时自增
  dict: ['1', '0', '2', '3', '5', '4', '6', '7', '8', '18', '9']
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
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
```

## 页面链接

### 关联表

- [[tables/ca_fee_company]]

### 字典

- [[dicts/ca_fee_order__company_type]]（`ca_fee_order.company_type`）
- [[dicts/ca_fee_order__order_type]]（`ca_fee_order.order_type`）
- [[dicts/ca_fee_order__order_status]]（`ca_fee_order.order_status`）
- [[dicts/ca_fee_order__annual_fee]]（`ca_fee_order.annual_fee`）
- [[dicts/ca_fee_order__pay_amount]]（`ca_fee_order.pay_amount`）
- [[dicts/ca_fee_order__pay_method]]（`ca_fee_order.pay_method`）
- [[dicts/ca_fee_order__bocom_plfm_bsn_id]]（`ca_fee_order.bocom_plfm_bsn_id`）
- [[dicts/ca_fee_order__bocom_txn_sts]]（`ca_fee_order.bocom_txn_sts`）
- [[dicts/ca_fee_order__agreement_version]]（`ca_fee_order.agreement_version`）
- [[dicts/ca_fee_order__agreement_signed]]（`ca_fee_order.agreement_signed`）
- [[dicts/ca_fee_order__invoice_status]]（`ca_fee_order.invoice_status`）
- [[dicts/ca_fee_order__version]]（`ca_fee_order.version`）
- [[dicts/ca_fee_order__enable]]（`ca_fee_order.enable`）
