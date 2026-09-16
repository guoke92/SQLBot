---
type: table
title: 立项字段历史
page_key: wechat_project_approval_field_history
domain: 微企链立项与项目审批
status: draft
anchors: [wechat_project_approval_field_history]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [wechat_project_stats]
---

# 立项字段历史

`apply_id` → 立项申请 id。非 SYNC 的 `change_source` 会保护字段不被企微同步覆盖。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[wechat_project_stats]]

`id`, `enable`, `create_time`, `update_time`, `apply_id`, `change_source`, `field_name`, `new_value`, `old_value`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `field_label`, `name`, `operator_id`, `operator_name`, `organization_id`, `remark`, `sp_no`

```ground:table
table: wechat_project_approval_field_history
database: lowcode_pplatform
desc: 项目立项字段更新历史
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [wechat_project_stats]
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
    group: always
    scenes: [wechat_project_stats]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [wechat_project_stats]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [wechat_project_stats]
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
  - name: apply_id
    type: number
    phys: bigint(20)
    desc: "申请id"
    roles: [query]
    scenes: [wechat_project_stats]
  - name: change_source
    type: string
    phys: varchar(64)
    desc: "变更来源"
    dict: change_source
    topk: "BATCH|EDIT|IMPORT|MANUAL_CREATE|SYNC"
    roles: [query]
    scenes: [wechat_project_stats]
  - name: field_name
    type: string
    phys: varchar(64)
    desc: "字段名"
    scenes: [wechat_project_stats]
  - name: new_value
    type: string
    phys: varchar(2000)
    desc: "新值"
    scenes: [wechat_project_stats]
  - name: old_value
    type: string
    phys: varchar(2000)
    desc: "旧值"
    scenes: [wechat_project_stats]
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "base"
  - name: field_label
    type: string
    phys: varchar(64)
    desc: "中文标签"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: operator_id
    type: string
    phys: varchar(64)
    desc: "操作人ID"
  - name: operator_name
    type: string
    phys: varchar(64)
    desc: "操作人姓名"
    topk: "caiweicheng|chenkaiwen|chenzerong|huangliyu3|linyanxiang|liubeicai|liuhaiou|liuning|ouyangpengfei|system-sync|xiaolonghao"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: sp_no
    type: string
    phys: varchar(64)
    desc: "审批编号"
```

```ground:relation
type: EQUI_JOIN
left: wechat_project_approval_field_history.apply_id
right: wechat_project_approval_apply.id
cardinality: many_to_one
status: proposed
evidence: code_path:FieldHistoryWriter.java
```
