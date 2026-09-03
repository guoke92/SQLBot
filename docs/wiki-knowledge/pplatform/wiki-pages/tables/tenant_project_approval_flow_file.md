---
type: table
title: 租户项目审批流程文件表
page_key: tenant_project_approval_flow_file
domain: 基线
status: draft
anchors: [tenant_project_approval_flow_file]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目审批流程文件表

（基线页：28 字段，行数估计 319。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_flow_file
database: lowcode_pplatform
desc: 租户项目审批流程文件表
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
  - name: busi_key
    type: string
    phys: varchar(64)
    desc: 业务key
  - name: catg_id
    type: string
    phys: varchar(64)
    desc: 影像分类编码
    topk: FBP_AGREEMENT|FBP_OA_ATTACHMENT|FBP_OA_COMMENT_FILE
  - name: catg_name
    type: string
    phys: varchar(64)
    desc: 影像分类名称
    topk: 审批备注追加文件|审批附件
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 114|1447805269378883586|1480444461854887938|1525044710953656322
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 1004|caiweicheng|chenkaiwen|chenzerong
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: file_id
    type: string
    phys: varchar(64)
    desc: 文件id
  - name: file_name
    type: string
    phys: varchar(64)
    desc: 文件名称
  - name: file_path
    type: string
    phys: varchar(1024)
    desc: 文件路径
  - name: file_url
    type: string
    phys: varchar(2048)
    desc: 文件url
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_tenant_project_approval_flow_file_comment
    type: string
    phys: varchar(128)
    desc: 关联项目审批
  - name: ref_tenant_project_approval_flow_file_project_approval
    type: string
    phys: varchar(128)
    desc: 关联项目审批
  - name: ref_tenant_project_approval_flow_file_project_approval_flow_node
    type: string
    phys: varchar(128)
    desc: 关联项目流程节点
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
    topk: 2193921079834066995|2193922587015270422|2193929646850986024|2193930827593695295
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 114|1447805269378883586|1480444461854887938|1525044710953656322
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 1004|caiweicheng|chenkaiwen|chenzerong
```

## 关联表

- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node → tenant_project_approval_flow_node.code（write-flow:ProjectApprovalDeskApplication.java，confirmed）
