---
type: table
title: CA服务费项目配置
page_key: ca_fee_project_config
domain: CA证书收费
status: draft
anchors: [ca_fee_project_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`ca_fee_project_config` 是**项目维度**的收费配置表，决定某个项目是否参与 CA 服务费收费、各角色年费标准以及特殊企业名单。它是规则引擎评估的第一道闸门（见 [[project_charge_switch]]），与订单表 [[ca_fee_order]]、企业主数据 [[ca_fee_company]] 构成「项目—订单—企业」三层结构。

`charge_enabled` 是收费总开关（口径见 [[project_charge_enabled]]）；`core_annual_fee`／`supplier_annual_fee` 是角色价，参与 [[annual_fee_pricing_chain]]；`special_company_list` 是特殊企业配置 JSON，承载 `WHITELIST`／`SPECIAL_PRICE`／`DEFER_PAY` 三类语义，其判定见 [[whitelist]]、[[whitelist_exempt]]、[[defer_pay_exempt]]；`pay_channel` 为支付渠道配置 JSON；`agreement_version` 为项目绑定收费协议版本；`enable` 为有效标识。

## 需求背景

收费能力按项目灰度：同一个企业可能在多个项目下有角色，是否收费取决于各项目自身的 `charge_enabled`，因此需要项目级配置源与项目级特殊名单，二者需与企业侧快照交叉校验（企业快照仅用于规则快速判断）。

## 版本演进

- v0（本页）：依据语义分析中 `evidence=code` 的字段清单建立契约。

```ground:table
table: ca_fee_project_config
database: lowcode_pplatform
desc: CA服务费项目配置
fields:
  - name: agreement_version
    type: string
    phys: varchar(64)
    desc: 当前绑定收费协议版本号
    dict: enable
    topk: "V1.0"
  - name: charge_enabled
    type: string
    phys: varchar(2)
    desc: 是否开启CA收费
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: pay_channel
    type: string
    phys: text
    desc: 缴费渠道JSON数组
    dict: enable
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
    topk: "GREENTOWNAT|JYYL|base|boscxsbl|boscxyc|sdhsg|shanghaiyinhang"
  - name: block_scene_list
    type: string
    phys: text
    desc: 拦截场景编码 JSON 数组，元素见 CaFeeInterceptSceneEnum
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: core_annual_fee
    type: number
    phys: int(10)
    desc: 核心企业角色年费（元）
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
  - name: last_toggle_time
    type: temporal
    phys: datetime
    desc: 最近一次收费开关切换时间
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 项目ID
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: special_company_list
    type: string
    phys: text
    desc: 特殊企业配置JSON数组
  - name: supplier_annual_fee
    type: number
    phys: int(10)
    desc: 供应商角色年费（元）
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 所属租户
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

- [[tenant_project]]：ca_fee_project_config.project_id → tenant_project.id（write-flow:CaFeeProjectConfigService.java，confirmed）
