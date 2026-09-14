---
type: table
title: 资方规则信息详情
page_key: funding_rule_detail
domain: 资金规则与异常处理
status: draft
anchors: [funding_rule_detail]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












明细表以「字段 key → 字段值」的 KV 形式存储一条资方规则的具体条目，归属 [[funding_rule_info]]（rule_info_id / fund_rule_code_ref 双挂靠）。字段 key 的跨表匹配语义见 [[rule_key]]，层级语义见 [[rule_layer]]。

## 需求背景

- 明细写入由 saveRuleInfo 与规则导入共同完成：命中已有 enable='Y' 的明细即更新，否则新增，见 [[rule_save_version_detail_sync]] 与 [[rule_import_four_stage_validation]]。
- 对外查询按 ruleLayer 分组为 UNDERLYING / FINANCING / OTHER，见 [[rule_provider_active_only]]。
- 产品维度与层级维度的实际落库分布见 [[funding_rule_detail_product_scope]]、[[funding_rule_detail_rule_layer_scope]]；check_scene 取值分布见 [[funding_rule_detail_check_scene_scope]]。

## 版本演进

v0 首次建立：字段语义取自 field_semantics（rule_key / rule_value / rule_layer / rule_info_id / fund_rule_code_ref / check_scene），`product_code`、`enable` 取自 calibers 证据。check_scene 在本主题 Application / Provider 均未见写值点，来源存疑，见 REVIEW 记录。语义分析未提供列类型，type 暂记为 `unknown`。

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
desc: 资方规则信息详情
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
  - name: rule_layer
    type: string
    phys: varchar(64)
    desc: 规则层
    dict: rule_layer
    topk: "FINANCING|OTHER|UNDERLYING"
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
  - name: check_scene
    type: string
    phys: varchar(64)
    desc: 校验场景
    topk: "SUBMIT_VALIDATE"
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
  - name: fund_rule_code_ref
    type: string
    phys: varchar(64)
    desc: 关联规则信息code
  - name: funding_party_mark
    type: string
    phys: varchar(64)
    desc: 资方标识
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
    phys: varchar(64)
    desc: 产品code
    topk: "ACFLOW|RVSFACTOR_PC"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: rule_info_id
    type: number
    phys: bigint(20)
    desc: 关系规则信息ID
  - name: rule_key
    type: string
    phys: varchar(64)
    desc: 字段key 对应front_key
  - name: rule_value
    type: string
    phys: varchar(64)
    desc: 规则值
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
    desc: 版本
```

## 关联表

- [[funding_rule_front_cfg]]：funding_rule_detail.rule_layer → funding_rule_front_cfg.rule_layer（copy:FundRuleInfoApplication.java，suggested）
- [[funding_rule_info]]：funding_rule_detail.rule_info_id → funding_rule_info.id（java-eq:FundRuleInfoApplication.java，suggested）
