---
type: table
title: CA服务费企业主数据
page_key: ca_fee_company
domain: CA证书收费
status: draft
anchors: [ca_fee_company]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`ca_fee_company` 是「CA证书收费」主题下的**企业维度主数据／台账主表**：以 `certification_no`（统一社会信用代码）为企业唯一键，一行代表一个企业在 CA 服务费语境下的缴费状态、CA 状态与服务周期。订单维度见 [[ca_fee_order]]，项目维度见 [[ca_fee_project_config]]。

表内语义分为四簇：① 身份与租户——`certification_no`、`company_name`、`db_tenant_code`、`enable`；② 状态——`pay_status`（企业级缴费汇总，见 [[ca_fee_company_pay_status]]）、`ca_status`（由签章中台状态归一化后同步，见 [[ca_fee_company_ca_status]]）；③ 服务期——`service_start`／`service_end`，由 [[ca_fee_order]] 的订单服务期快照回写，续费提醒与到期刷新见 [[renewal_remind_expire]]；④ 定价与特殊配置——`source_project_id`／`source_company_type` 记录首次锁定来源，`locked_annual_fee`／`fee_locked` 记录首次缴费成功后锁定的年费标准，`special_annual_fee`／`special_config_flag` 承载生效中的特殊配置快照，`renew_remind_sent` 控制本期续费待办是否已生成。定价优先级见 [[annual_fee_pricing_chain]]，白名单判定见 [[whitelist_exempt]]。

`enable = 'Y'` 是台账查询、规则引擎与快照的有效性前提，口径见 [[company_enable_valid]]。

## 需求背景

CA 服务费按「一企一行」沉淀企业主数据，使同一企业在多个项目、多个角色（`CORE`／`SUPPLIER`／`PROJECT_COMPANY`）下的缴费结论可以汇总为单一状态，避免以订单行替代企业状态导致的重复计费。企业级 `pay_status` 与订单级 `order_status` 的分工见 [[pending_payment]]、[[paid_payment]]。

## 版本演进

- v0（本页）：依据语义分析中 `evidence=db` 的字段清单建立首版字段契约，未引入未证实主张。

```ground:table
table: ca_fee_company
database: lowcode_pplatform
desc: CA服务费企业主数据
fields:
  - name: ca_status
    type: string
    phys: varchar(64)
    desc: CA签章状态
    dict: ca_status
    topk: "CANCELLED|NORMAL|UNKNOWN"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: fee_locked
    type: string
    phys: varchar(2)
    desc: 是否已锁定年费标准
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: pay_status
    type: string
    phys: varchar(64)
    desc: 缴费状态：PAID 已缴费 / UNPAID 未缴费
    dict: pay_status
    topk: "PAID|UNPAID"
    labels: "PAID:已缴费|UNPAID:未缴费"
  - name: renew_remind_sent
    type: string
    phys: varchar(2)
    desc: 本期续费待办是否已生成：Y 已生成 / N 未生成
    dict: enable
    topk: "N|Y"
    labels: "N:未生成|Y:已生成"
  - name: source_company_type
    type: string
    phys: varchar(128)
    desc: 首次锁定来源企业角色，如 SUPPLIER/CORE
    dict: source_company_type
    topk: "CORE|PROJECT_COMPANY|SUPPLIER"
  - name: special_config_flag
    type: string
    phys: varchar(2)
    desc: 是否存在生效中的特殊配置快照
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统一社会信用代码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
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
  - name: ext_json
    type: string
    phys: text
    desc: 扩展字段 JSON预留
  - name: locked_annual_fee
    type: number
    phys: int(10)
    desc: 首次缴费成功后锁定的年费标准（元）
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: service_end
    type: temporal
    phys: date
    desc: 当前 CA 服务费服务周期截止日（含）
  - name: service_start
    type: temporal
    phys: date
    desc: 当前 CA 服务费服务周期起始日（含）
  - name: source_project_id
    type: number
    phys: bigint(20)
    desc: 首次锁定来源项目 ID
  - name: special_annual_fee
    type: number
    phys: int(10)
    desc: 特殊配置后应缴年费（元）
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 首次锁定来源租户
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
```

## 关联表

- [[ca_fee_order]]：ca_fee_company.certification_no → ca_fee_order.certification_no（java-eq-same:CaFeeLedgerQueryService.java，suggested）
- [[ca_fee_order]]：ca_fee_company.company_name → ca_fee_order.company_name（copy:CaFeeOrderService.java，suggested）
- [[ca_fee_order]]：ca_fee_company.service_end → ca_fee_order.service_end（copy:CaFeeOrderService.java，suggested）
- [[ca_fee_order]]：ca_fee_company.service_start → ca_fee_order.service_start（copy:CaFeeOrderService.java，suggested）
- [[ca_fee_order]]：ca_fee_company.source_project_id → ca_fee_order.project_id（write-flow:CaFeeOrderService.java，confirmed）
- [[cust_project_rel]]：ca_fee_company.code → cust_project_rel.ref_cust_project_rel_cust_company_info（java-eq:CaFeeRuleEngineService.java，suggested）
