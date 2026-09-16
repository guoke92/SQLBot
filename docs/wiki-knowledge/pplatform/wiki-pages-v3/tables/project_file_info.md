---
type: table
title: 项目运营文件
page_key: project_file_info
domain: 文件/附件/媒体
status: draft
anchors: [project_file_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [tenant_project]
---

# 项目运营文件

`project_id` → [[tenant_project]].id。`file_type` 库值为 cust/approve/check/collate/other，没有 Java 枚举类。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[tenant_project]]

`id`, `enable`, `create_time`, `update_time`, `file_type`, `project_id`, `title`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `content`, `db_tenant_code`, `name`, `organization_id`, `remark`

```ground:table
table: project_file_info
database: lowcode_pplatform
desc: 项目运营文件管理
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [tenant_project]
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
    scenes: [tenant_project]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [tenant_project]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [tenant_project]
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
  - name: file_type
    type: string
    phys: varchar(32)
    desc: "文件类型"
    topk: "approve|check|collate|cust|other"
    roles: [query]
    scenes: [tenant_project]
  - name: project_id
    type: number
    phys: bigint(20)
    desc: "项目id"
    roles: [query]
    scenes: [tenant_project]
  - name: title
    type: string
    phys: varchar(200)
    desc: "标题"
    scenes: [tenant_project]
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
  - name: content
    type: string
    phys: varchar(500)
    desc: "描述"
    topk: "1|10|11|123|2|22|222|2342342|3|3232424|4|5|6|7|8|9|aaa|描述1"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```

```ground:relation
type: EQUI_JOIN
left: project_file_info.project_id
right: tenant_project.id
cardinality: many_to_one
status: proposed
evidence: code_path:ProjectFileController.java
```
