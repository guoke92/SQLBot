---
type: table
title: 项目立项字段更新历史
page_key: wechat_project_approval_field_history
belong: tables
domain: 基线
status: draft
anchors: [wechat_project_approval_field_history]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 项目立项字段更新历史

（基线页：27 字段，行数估计 1515。行语义/常用过滤待语义摄取增强。）

```ground:table
table: wechat_project_approval_field_history
database: lowcode_pplatform
desc: 项目立项字段更新历史
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
  - name: apply_id
    type: number
    phys: bigint(20)
    desc: 关联 wechat_project_approval_apply.id
  - name: change_source
    type: string
    phys: varchar(64)
    desc: 变更来源
    topk: BATCH|EDIT|IMPORT|MANUAL_CREATE
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1480444461854887938|1534087161817419777|1631538947253182466|1761948088379621378
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: caiweicheng|chenkaiwen|chenzerong|huangliyu3
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: base
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: field_label
    type: string
    phys: varchar(64)
    desc: 中文标签
  - name: field_name
    type: string
    phys: varchar(64)
    desc: 列名
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: new_value
    type: string
    phys: varchar(2000)
    desc: 变更后值
  - name: old_value
    type: string
    phys: varchar(2000)
    desc: 变更前值
  - name: operator_id
    type: string
    phys: varchar(64)
    desc: 操作人ID
    topk: 1480444461854887938|1534087161817419777|1631538947253182466|1761948088379621378
  - name: operator_name
    type: string
    phys: varchar(64)
    desc: 操作人姓名
    topk: caiweicheng|chenkaiwen|chenzerong|huangliyu3
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sp_no
    type: string
    phys: varchar(64)
    desc: 审批编号
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1480444461854887938|1534087161817419777|1631538947253182466|1761948088379621378
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: caiweicheng|chenkaiwen|chenzerong|huangliyu3
```
