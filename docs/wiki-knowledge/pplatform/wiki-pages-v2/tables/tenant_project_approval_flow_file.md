---
type: table
title: 租户项目审批流程文件表
page_key: tenant_project_approval_flow_file
domain: 微企链立项与项目审批
status: draft
anchors: [tenant_project_approval_flow_file]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












上线审批流程中的影像/附件记录表，按影像分类挂载在审批流程上；重新发起审批时影像文件会随主记录一并复制，见 [[rules/reinitiate_online_approval_copy]]。

```ground:table
table: tenant_project_approval_flow_file
database: lowcode_pplatform
desc: 租户项目审批流程文件表
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
  - name: busi_key
    type: string
    phys: varchar(64)
    desc: 业务key
  - name: catg_id
    type: string
    phys: varchar(64)
    desc: 影像分类编码
  - name: catg_name
    type: string
    phys: varchar(64)
    desc: 影像分类名称
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
    topk: "ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2|beehive-scf.qhhrly.cn|ning|spsi.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
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

- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node → tenant_project_approval_flow_node.code（write-flow:ProjectApprovalDeskApplication.java，confirmed）
- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval → tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval（write-flow:ProjectApprovalDeskApplication.java，confirmed）
## 需求背景

影像分类用于区分商务批复报价文件、项目配置附件与 OA 附件等不同用途的文件；提交上线审批时要求必须上传商务批复报价文件，见 [[rules/online_approval_submit]]。

## 版本演进

影像分类取值呈现「代码枚举 < DB 实际分布」的缺口：`FBP_OA_ATTACHMENT`、`FBP_OA_COMMENT_FILE` 出现在数据中但未在代码枚举声明，分类枚举的完整基线待补齐。
