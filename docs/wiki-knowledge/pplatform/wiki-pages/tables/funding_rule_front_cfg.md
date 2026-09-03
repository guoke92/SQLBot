---
type: table
title: 资方规则前端配置页面
page_key: funding_rule_front_cfg
domain: 基线
status: draft
anchors: [funding_rule_front_cfg]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 资方规则前端配置页面

（基线页：27 字段，行数估计 47。行语义/常用过滤待语义摄取增强。）

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
desc: 资方规则前端配置页面
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: rule_layer
    type: string
    phys: varchar(64)
    desc: 规则层 UNDERLYING/FINANCING
    dict: rule_layer
    topk: FINANCING|OTHER|UNDERLYING
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
    topk: SUBMIT_VALIDATE
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
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
    topk: 企业注册年限校验|合同名称是否必填
  - name: key_name
    type: string
    phys: varchar(64)
    desc: 字段名称描述
    topk: 企业注册年限校验|合同名称是否必填
  - name: key_type
    type: string
    phys: varchar(32)
    desc: 字段业务规则类型
    topk: DATE_CHECK_NATURAL|DATE_CHECK_WORKDAY|FIELD_LENGTH_LIMIT|FIELD_REQUIRED
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
    topk: ACFLOW|RVSFACTOR_PC
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: rule_key
    type: string
    phys: varchar(64)
    desc: 规则字段key
    topk: B0003|baseContName|baseContNo|contractAmount
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```
