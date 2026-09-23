---
type: table
title: CA服务费订单
page_key: ca_fee_order
belong: tables
status: draft
anchors:
- ca_fee_order
sources:
- database_schema:lowcode_pplatform.ca_fee_order
- code_path:CaFeeOrderBizMapper.java:13
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- ca_fee_company
- ca_fee_special_config
- cust_company_info
- tenant_project
- tenant_setting_config
- ca_fee_order__company_type
- ca_fee_order__order_type
- ca_fee_order__order_status
- ca_fee_order__agreement_signed
- ca_fee_order__invoice_status
- ca_fee_order__enable
- ca_fee_order__pay_method
---
# CA服务费订单

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: ca_fee_order
database: lowcode_pplatform
desc: CA服务费订单
inactive: false
primary_key:
- id
grain: 一订单号一行
name_anchors:
- company_name
- project_name
- code
- name
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
  dict:
  - SUPPLIER
  - CORE
  - PROJECT_COMPANY
  label:
    SUPPLIER: 供应商
    CORE: 核心企业
- name: order_type
  type: string
  desc: 订单类型
  dict:
  - STOCK
  - FIRST
  - RENEW_EXPIRED
  - RENEW
  label:
  - 存量补录
  - 首次缴费
  - 已到期续费
  - 即将到期续费
- name: order_status
  type: string
  desc: 订单状态
  dict:
  - CLOSED
  - PENDING
  - PAID
  - PAIDING
  - UNPAID
  - EXPIRED
  label:
    CLOSED: 已关闭
    PENDING: 未缴费
    PAID: 已缴费
    EXPIRED: 已过期
  written_with:
  - pay_amount
  - pay_time
  - service_start
  - service_end
- name: annual_fee
  type: number
  desc: 应缴年费（元）
- name: pay_amount
  type: number
  desc: 实缴金额（元）
  written_with:
  - order_status
  - pay_time
  - service_start
  - service_end
- name: pay_method
  type: string
  desc: 支付方式
  dict:
  - BOCOM
  label:
  - 交e保对公打款
- name: pay_remark
  type: string
  desc: 打款备注
- name: pay_time
  type: temporal
  desc: 缴费成功时间
  written_with:
  - order_status
  - pay_amount
  - service_start
  - service_end
- name: bocom_plfm_ser_no
  type: string
  desc: 交e保平台流水号
- name: bocom_plfm_bsn_id
  type: string
  desc: 平台业务编号
- name: bocom_req_sn
  type: string
  desc: 请求流水号
- name: bocom_txn_sts
  type: string
  desc: 响应状态
- name: service_start
  type: temporal
  desc: 本单服务周期起始日（含）
  written_with:
  - order_status
  - pay_amount
  - pay_time
  - service_end
- name: service_end
  type: temporal
  desc: 本单服务周期截止日（含）
  written_with:
  - order_status
  - pay_amount
  - pay_time
  - service_start
- name: agreement_version
  type: string
  desc: 签署时绑定的收费协议版本号
- name: agreement_signed
  type: string
  desc: 是否已签署收费协议
  dict:
  - N
  - Y
  label:
    N: 否
    Y: 是
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
  dict:
  - PENDING
  - ISSUED
  - FAILED
  - NONE
  label:
  - 开票中
  - 已开票
  - 开票失败
  - 无需开票
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
  predicate: ca_fee_order.enable = 'Y'
  trust: confirmed
  evidence: code_path:CaFeeOrderBizMapper.java:13
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: ca_fee_order.project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeOrderService.java:150
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: ca_fee_order.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeOrderService.java:481
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: ca_fee_order.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CaFeeBocomGateway.java:118
source: l1_code
join_role: identity
priority: primary
authenticity_note: company_id 是企业主键，不是 ca_fee_company.id。
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
left: cust_company_info.certification_no
right: ca_fee_order.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: 'live_validate:fk_like;collide_refine:promoted: ca_fee_order.certification_no
  ⊆ cust_company_info.certification_no'
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 'promoted: ca_fee_order.certification_no ⊆ cust_company_info.certification_no'
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

## 页面链接

### 关联表

- [[tables/ca_fee_company]]
- [[tables/ca_fee_special_config]]
- [[tables/cust_company_info]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]

### 概念

- [[concepts/ca_fee_paid]]
- [[concepts/certification_no_term]]

### 字典

- [[dicts/ca_fee_order__company_type]]（`ca_fee_order.company_type`）
- [[dicts/ca_fee_order__order_type]]（`ca_fee_order.order_type`）
- [[dicts/ca_fee_order__order_status]]（`ca_fee_order.order_status`）
- [[dicts/ca_fee_order__pay_method]]（`ca_fee_order.pay_method`）
- [[dicts/ca_fee_order__agreement_signed]]（`ca_fee_order.agreement_signed`）
- [[dicts/ca_fee_order__invoice_status]]（`ca_fee_order.invoice_status`）
- [[dicts/ca_fee_order__enable]]（`ca_fee_order.enable`）
