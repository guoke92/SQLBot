---
type: table
title: 资方规则明细
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
contract_version: "0.3"
belong: tables
scenes: [funding_rules]
---

# 资方规则明细

`rule_info_id` → [[funding_rule_info]].id。`rule_layer` 库值 UNDERLYING/FINANCING/OTHER。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[funding_rules]]

`id`, `enable`, `create_time`, `update_time`, `rule_info_id`, `rule_layer`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `check_scene`, `db_tenant_code`, `fund_rule_code_ref`, `funding_party_mark`, `name`, `organization_id`, `product_code`, `remark`, `rule_key`, `rule_value`, `version`

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
desc: 资方规则信息详情
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [funding_rules]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    roles: [query]
    group: always
    scenes: [funding_rules]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [funding_rules]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [funding_rules]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: rule_info_id
    type: number
    phys: bigint(20)
    desc: "规则头id"
    roles: [query]
    scenes: [funding_rules]
  - name: rule_layer
    type: string
    phys: varchar(64)
    desc: "规则层"
    topk: "FINANCING|OTHER|UNDERLYING"
    roles: [query]
    scenes: [funding_rules]
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: check_scene
    type: string
    phys: varchar(64)
    desc: "校验场景"
    topk: "SUBMIT_VALIDATE"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: fund_rule_code_ref
    type: string
    phys: varchar(64)
    desc: "关联规则信息code"
  - name: funding_party_mark
    type: string
    phys: varchar(64)
    desc: "资方标识"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: product_code
    type: string
    phys: varchar(64)
    desc: "产品code"
    topk: "ACFLOW|RVSFACTOR_PC"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: rule_key
    type: string
    phys: varchar(64)
    desc: "字段key 对应front_key"
  - name: rule_value
    type: string
    phys: varchar(64)
    desc: "规则值"
  - name: version
    type: number
    phys: int(10)
    desc: "版本"
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.rule_info_id
right: funding_rule_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:FundRuleInfoApplication.java
```
