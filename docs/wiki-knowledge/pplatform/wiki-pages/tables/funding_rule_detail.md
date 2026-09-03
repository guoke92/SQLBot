---
type: table
title: 资方规则信息详情
page_key: funding_rule_detail
domain: 基线
status: draft
anchors: [funding_rule_detail]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 资方规则信息详情

（基线页：27 字段，行数估计 1488。行语义/常用过滤待语义摄取增强。）

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
desc: 资方规则信息详情
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: rule_layer
    type: string
    phys: varchar(64)
    desc: 规则层
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
    topk: base
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
    topk: 1207485686830276611|1428547222588211202|1470596729829560321|1480444461854887938
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: chenkaiwen|glr|wudongyang|丁铁
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
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
    topk: ACFLOW|RVSFACTOR_PC
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
    topk: 1207485686830276611|1428547222588211202|1470596729829560321|1480444461854887938
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: chenkaiwen|glr|wudongyang|丁铁
  - name: version
    type: number
    phys: int(10)
    desc: 版本
    topk: 1|11|17|2
```

## 关联表

- [[funding_rule_info]]：funding_rule_detail.rule_info_id → funding_rule_info.id（java-eq:FundRuleInfoApplication.java，suggested）
