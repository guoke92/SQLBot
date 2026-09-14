---
type: table
title: 资方规则前端配置页面
page_key: funding_rule_front_cfg
domain: 资金规则与异常处理
status: draft
anchors: [funding_rule_front_cfg]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表是规则字段的配置字典：定义前端字段 key、字段名称、字段业务规则类型与所属层级，是导入与详情回显时定位字段的权威来源。导入按 (product, rule_layer, key_name) 三元组反查 front_key，规则保存时以 ruleMap.key 匹配 frontKey，见 [[rule_import_four_stage_validation]]、[[rule_save_version_detail_sync]]。

## 需求背景

- 导入阶段 4 需要把规则层级的 displayName 翻译为 dictKey，并借本表拿到 frontKey；产品无前端配置时保存直接抛异常（见 [[rule_save_version_detail_sync]]）。
- 本表的 rule_layer 与明细的 rule_layer 同值但非外键，见 [[rule_layer]]；front_key / rule_key 的三种用法差异见 [[rule_key]]。

## 版本演进

v0 首次建立：字段语义取自 field_semantics（front_key / key_name / key_type / rule_key），`rule_layer` 取自 term_bridges 的边界描述，`enable` 取自 calibers 证据 [[funding_rule_front_cfg_enable_y]]。语义分析未提供列类型，type 暂记为 `unknown`。

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
desc: 资方规则前端配置页面
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
  - name: key_type
    type: string
    phys: varchar(32)
    desc: 字段业务规则类型
    dict: key_type
    topk: "DATE_CHECK_NATURAL|DATE_CHECK_WORKDAY|FIELD_LENGTH_LIMIT|FIELD_REQUIRED|FILE_COUNT_LIMIT|FILE_NAME_SYMBOL|FILE_SIZE_PACKAGE_LIMIT|FILE_SIZE_SINGLE_LIMIT|FILE_SIZE_TOTAL_LIMIT|FILE_TYPE_LIMIT|INVOICE_COUNT_LIMIT|YEARS_CHECK"
  - name: rule_layer
    type: string
    phys: varchar(64)
    desc: 规则层 UNDERLYING/FINANCING
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
  - name: front_field_style
    type: string
    phys: varchar(512)
    desc: 前端字段渲染json
  - name: front_key
    type: string
    phys: varchar(100)
    desc: 前端字段key
  - name: front_key_name
    type: string
    phys: varchar(128)
    desc: 前端展示字段名称
  - name: key_name
    type: string
    phys: varchar(64)
    desc: 字段名称描述
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
  - name: rule_key
    type: string
    phys: varchar(64)
    desc: 规则字段key
    topk: "B0003|baseContName|baseContNo|contractAmount|contractDate|foundedDate|list.contractAmount|list.contractDate|list.contractName|list.contractNo|transferDate"
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

- [[funding_rule_detail]]：funding_rule_front_cfg.rule_layer → funding_rule_detail.rule_layer（copy:FundRuleInfoApplication.java，suggested）
