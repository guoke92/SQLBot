---
type: table
title: 资方规则信息
page_key: funding_rule_info
domain: 资金规则与异常处理
status: draft
anchors: [funding_rule_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表是资方规则的头表：以「产品 code + 资方标识」定位一条规则，承载规则状态、版本号与规则编码 `code`，明细行由 [[funding_rule_detail]] 通过 rule_info_id / fund_rule_code_ref 挂靠。资方标识在本域的表达见 [[funding_party_mark]]。

## 需求背景

- 新增规则默认待生效、更新时版本自增，随后与明细联动，见 [[rule_save_version_detail_sync]]。
- 对外只暴露已生效规则，见 [[rule_provider_active_only]]。
- 规则导入的资方合法性校验目前硬编码按 ACFLOW 产品名单执行，与落库产品并存存在语义张力，见 [[rule_import_funding_party_hardcoded]]。
- 列表/导出宣称支持时间区间，实际条件被注释掉，见 [[rule_export_ignore_time_range]]。

## 版本演进

v0 首次建立：核心字段语义取自 field_semantics（funding_party_mark / rule_status / version / code），`enable`、`product_code`、`funding_party_name` 的语义取自 calibers 与 rules 的证据，一并纳入本页。状态取值与流转见 [[funding_rule_status_machine]]，状态枚举审计口径见 [[funding_rule_info_enable_y]]。语义分析未提供列类型，type 暂记为 `unknown`。

```ground:table
table: funding_rule_info
database: lowcode_pplatform
desc: 资方规则信息
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: rule_status
    type: string
    phys: varchar(64)
    desc: 规则状态 ACTIVE/INACTIVE/PENDING
    dict: rule_status
    topk: "ACTIVE|INACTIVE|PENDING"
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
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
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
  - name: funding_party_mark
    type: string
    phys: varchar(64)
    desc: 资金方标识
  - name: funding_party_name
    type: string
    phys: varchar(100)
    desc: 资方名称
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_code
    type: string
    phys: varchar(32)
    desc: 产品code
    topk: "ACFLOW|RVSFACTOR_PC"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
    desc: 版本号
```

## 关联表

- [[funding_rule_detail]]：funding_rule_info.id → funding_rule_detail.rule_info_id（java-eq:FundRuleInfoApplication.java，suggested）
