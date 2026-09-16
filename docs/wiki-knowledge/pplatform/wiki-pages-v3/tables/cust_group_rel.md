---
type: table
title: 集团成员关系
page_key: cust_group_rel
domain: 企业银行账户/集团/SFTP
status: draft
anchors: [cust_group_rel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_group]
---

# 集团成员关系

`cust_id` / `parent_cust_id` / `root_cust_id` → [[cust_company_info]].id。`cust_type` 写入时从企业角色拷贝。`root_flag` 列注释：Y 是 / N 不是。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_group]]

`id`, `enable`, `create_time`, `update_time`, `cust_id`, `cust_type`, `level`, `parent_cust_id`, `root_cust_id`, `root_flag`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `name`, `organization_id`, `parent_group_id`, `remark`, `root_group_id`

```ground:table
table: cust_group_rel
database: lowcode_pplatform
desc: 集团成员单位关系表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    roles: [query, result]
    group: always
    scenes: [company_group]
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
    scenes: [company_group]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    roles: [result]
    group: always
    scenes: [company_group]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    roles: [result]
    group: always
    scenes: [company_group]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    roles: [result]
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    roles: [result]
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    roles: [result]
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    roles: [result]
    group: always
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    roles: [query]
    scenes: [company_group]
  - name: cust_type
    type: string
    phys: varchar(256)
    desc: "企业角色 多企业角色用逗号分隔"
    dict: cust_type
    labels: "1:个人客户|2:企业客户|3:运营方企业客户|4:企业客户"
    roles: [query, result]
    scenes: [company_group]
  - name: level
    type: number
    phys: int(10)
    desc: "层级"
    topk: "1"
    labels: "1:是"
    scenes: [company_group]
  - name: parent_cust_id
    type: number
    phys: bigint(20)
    desc: "父企业id"
    roles: [query]
    scenes: [company_group]
  - name: root_cust_id
    type: number
    phys: bigint(20)
    desc: "根企业id"
    roles: [query]
    scenes: [company_group]
  - name: root_flag
    type: string
    phys: varchar(4)
    desc: "是否集团企业"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    scenes: [company_group]
  - name: status
    type: string
    phys: varchar(256)
    desc: "状态"
    dict: group_rel_status
    topk: "EFFECTIVE|INEFFECTIVE|REJECTED"
    roles: [query]
    scenes: [company_group]
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
    topk: "ISOLATE_TAG_CJTZ|ISOLATE_TAG_HBCI|ISOLATE_TAG_HBLT|ISOLATE_TAG_hylg|ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_yccsfzjt|LN1|LN2|QA2tiepai2|beehive-scf.qhhrly.cn|eascs.beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|sny|spsi.beehive-scf.qhhrly.cn|tianma.beehive-scf.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    roles: [query, result]
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: parent_group_id
    type: number
    phys: bigint(20)
    desc: "父id"
    roles: [query, result]
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: root_group_id
    type: number
    phys: bigint(20)
    desc: "根id"
    roles: [query, result]
```

```ground:relation
type: EQUI_JOIN
left: cust_group_rel.cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CustGroupMapper.xml
```

```ground:relation
type: EQUI_JOIN
left: cust_group_rel.parent_cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CustGroupMapper.xml
```

```ground:relation
type: EQUI_JOIN
left: cust_group_rel.root_cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CustGroupMapper.xml
```
