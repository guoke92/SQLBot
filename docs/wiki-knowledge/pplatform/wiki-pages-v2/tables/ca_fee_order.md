---
type: table
title: CA服务费订单
page_key: ca_fee_order
domain: CA证书收费
status: draft
anchors: [ca_fee_order]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`ca_fee_order` 是**订单维度**的收费单据表，一行代表一次首次缴费、续费或存量补录行为，业务标识为 `order_no`（见 [[fee_order]]）。企业维度的汇总状态在 [[ca_fee_company]]，项目维度的收费开关与费率在 [[ca_fee_project_config]]。

关键分组：① 生命周期——`order_status`（见 [[ca_fee_order_status]]）、`close_reason`、`order_type`（FIRST／RENEW／RENEW_EXPIRED／STOCK）；② 协议——`agreement_signed`（见 [[ca_fee_order_agreement_signed]]、[[fee_agreement]]）、`agreement_version`；③ 金额与支付——`annual_fee`、`pay_amount`、`pay_method`（当前主要支持 `BOCOM` 交e保，见 [[bocom]]）、`pay_time`；④ 服务期快照——`service_start`／`service_end`，是企业主数据当前服务期的来源（见 [[service_period]]）；⑤ 发票——`invoice_status`（见 [[ca_fee_order_invoice_status]]）；⑥ 交e保渠道字段——`bocom_txn_sts`（`00`／`01`／`02`）、`bocom_plfm_ser_no`、`bocom_plfm_bsn_id`、`bocom_req_sn`，幂等与查证逻辑见 [[bocom_idempotent_verify]]；⑦ 归属——`project_id`、`company_id`、`company_type`（`CORE`／`SUPPLIER`／`PROJECT_COMPANY`）。

订单是协议签署、支付、开票、台账编辑等可操作动作的最小载体，因此绝大多数限制性规则（[[agreement_sign_prerequisite]]、[[ledger_edit_limit]]）都落在 `order_status` 与 `bocom_txn_sts` 上。

## 需求背景

订单与企业主数据解耦，使「一次缴费」与「当前服务期」分别可追溯：订单保留签署时的协议版本与年费金额快照，企业主数据只保留当前有效结论。年费标准由 [[annual_fee_pricing_chain]] 解析后写入本表 `annual_fee`。

## 版本演进

- v0（本页）：依据语义分析字段清单建立契约；`EXPIRED` 状态枚举存在但未使用，按订单状态机页标注为「未使用」。

```ground:table
table: ca_fee_order
database: lowcode_pplatform
desc: CA服务费订单
fields:
  - name: agreement_signed
    type: string
    phys: varchar(2)
    desc: 是否已签署收费协议
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: bocom_txn_sts
    type: string
    phys: varchar(64)
    desc: 响应状态
    dict: bocom_txn_sts
    topk: "00"
  - name: company_type
    type: string
    phys: varchar(64)
    desc: 企业角色：SUPPLIER/CORE
    dict: ca_fee_order__company_type
    topk: "CORE|PROJECT_COMPANY|SUPPLIER"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: invoice_status
    type: string
    phys: varchar(64)
    desc: 发票状态
    dict: invoice_status
    topk: "ISSUED|PENDING"
  - name: order_status
    type: string
    phys: varchar(64)
    desc: 订单状态
    dict: order_status
    topk: "CLOSED|PAID|PAIDING|PENDING|UNPAID"
  - name: order_type
    type: string
    phys: varchar(64)
    desc: 订单类型
    dict: order_type
    topk: "FIRST|RENEW|RENEW_EXPIRED|STOCK"
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: agreement_file_path
    type: string
    phys: varchar(2048)
    desc: 签章后协议文件 COS 路径
  - name: agreement_sign_time
    type: temporal
    phys: datetime
    desc: 收费协议签署时间
  - name: agreement_version
    type: string
    phys: varchar(64)
    desc: 签署时绑定的收费协议版本号
    topk: "V1.0"
  - name: annual_fee
    type: number
    phys: int(10)
    desc: 应缴年费（元）
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: bocom_pay_info
    type: string
    phys: text
    desc: 交e保虚拟户快照JSON
  - name: bocom_plfm_bsn_id
    type: string
    phys: varchar(128)
    desc: 平台业务编号
  - name: bocom_plfm_ser_no
    type: string
    phys: varchar(128)
    desc: 交e保平台流水号
  - name: bocom_req_sn
    type: string
    phys: varchar(128)
    desc: 请求流水号
  - name: certification_no
    type: string
    phys: varchar(64)
    desc: 统一社会信用代码
  - name: close_reason
    type: string
    phys: varchar(1024)
    desc: 关闭原因（关开关/手动关闭等）
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业 ID
  - name: company_name
    type: string
    phys: varchar(512)
    desc: 企业名称
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "ISOLATE_TAG_boscebl|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn|xylxchf"
  - name: invoice_fail_reason
    type: string
    phys: varchar(64)
    desc: 开票失败原因
  - name: invoice_file_path
    type: string
    phys: varchar(2048)
    desc: 发票PDF 文件COS路径
  - name: invoice_no
    type: string
    phys: varchar(128)
    desc: 发票号码
  - name: invoice_request_id
    type: string
    phys: varchar(256)
    desc: 开票平台请求号
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: operate_logs
    type: string
    phys: text
    desc: 操作轨迹 JSON 数组
  - name: order_no
    type: string
    phys: varchar(128)
    desc: 订单号，唯一键
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pay_amount
    type: number
    phys: int(10)
    desc: 实缴金额（元）
  - name: pay_method
    type: string
    phys: varchar(64)
    desc: 支付方式
    topk: "BOCOM"
  - name: pay_remark
    type: string
    phys: varchar(512)
    desc: 打款备注
  - name: pay_time
    type: temporal
    phys: datetime
    desc: 缴费成功时间
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 触发项目 ID
  - name: project_name
    type: string
    phys: varchar(512)
    desc: 项目名称
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: service_end
    type: temporal
    phys: date
    desc: 本单服务周期截止日（含）
  - name: service_start
    type: temporal
    phys: date
    desc: 本单服务周期起始日（含）
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 所属租户 ID
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: version
    type: number
    phys: int(10)
    desc: 乐观锁版本号，更新订单状态时自增
```

## 关联表

- [[ca_fee_company]]：ca_fee_order.certification_no → ca_fee_company.certification_no（java-eq-same:CaFeeLedgerQueryService.java，suggested）
- [[ca_fee_company]]：ca_fee_order.company_name → ca_fee_company.company_name（copy:CaFeeOrderService.java，suggested）
- [[ca_fee_company]]：ca_fee_order.project_id → ca_fee_company.source_project_id（write-flow:CaFeeOrderService.java，confirmed）
- [[ca_fee_company]]：ca_fee_order.service_end → ca_fee_company.service_end（copy:CaFeeOrderService.java，suggested）
- [[ca_fee_company]]：ca_fee_order.service_start → ca_fee_company.service_start（copy:CaFeeOrderService.java，suggested）
