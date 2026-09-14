---
type: table
title: 集团成员单位关系表
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
contract_version: "0.1"
belong: tables
---












# 集团成员单位关系表

`cust_group_rel` 描述集团与其成员单位之间的树形关系：一行记录代表“当前成员企业（`cust_id`）”上挂到“上一级企业（`parent_cust_id`）”的那条关系，同时冗余根集团企业（`root_cust_id`）与根节点（`root_group_id`）用于整树检索。`parent_group_id`/`root_group_id` 自引用本表 `id`，建树时按 `parent_group_id` 分组。

## 需求背景

集团关系需要支持多级建树与按根节点拉平（`listAllNodesByRootId`）、按 `db_tenant_code` 做租户隔离。成员单位关系的生效依赖签署流程：新增关系先落未生效（[[cust_group_rel_status]]），发送签署待办（[[notice_no_duplicate]]、[[async_notice_tolerant]]）；根节点不允许再签署/拒绝（[[root_group_no_operation]]）；删除成员单位前必须做在途业务校验（[[member_remove_check_business]]）；导入时同一上级下成员单位角色必须一致（[[member_role_consistency]]）。

## 版本演进

- `cust_type` 以 JSON 数组字符串落库（代码用 `JSONArray.toJSONString()` 写入，形如 `["CORE"]`），支持多角色逐条写入，见 [[enterprise_role]]。
- `level` 代码仅在根节点写入 `1`，DB 实测仅出现 `'1'`；`root_flag='Y'` 29 条与 `level=1` 的 29 条一致。
- 关系状态取值为 EFFECTIVE/INEFFECTIVE/REJECTED，见 [[cust_group_rel_status]]。
- 需求文档另有“企业状态流转：待提交→审核中→已通过；已通过→已冻结/已注销”的主张，代码侧未被证实，见 [[cust_group_rel_status]] 版本演进说明。

```ground:table
table: cust_group_rel
database: lowcode_pplatform
desc: 集团成员单位关系表
fields:
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
    roles: [query, result]
  - name: cust_type
    type: string
    phys: varchar(256)
    desc: 企业角色 多企业角色用逗号分隔
    dict: cust_type
    roles: [query, result]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    roles: [query, result]
  - name: parent_group_id
    type: number
    phys: bigint(20)
    desc: 父id
    roles: [query, result]
  - name: root_cust_id
    type: number
    phys: bigint(20)
    desc: 根企业id
    roles: [query, result]
  - name: root_group_id
    type: number
    phys: bigint(20)
    desc: 根id
    roles: [query, result]
  - name: root_flag
    type: string
    phys: varchar(4)
    desc: 是否集团企业 Y:是 N:不是
    dict: enable
    topk: "N|Y"
    labels: "N:不是|Y:是"
  - name: status
    type: string
    phys: varchar(256)
    desc: 状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED
    dict: cust_group_rel__status
    topk: "EFFECTIVE|INEFFECTIVE|REJECTED"
    labels: "EFFECTIVE:未生效|INEFFECTIVE:已拒绝"
    roles: [result]
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
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    roles: [result]
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    roles: [result]
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "ISOLATE_TAG_CJTZ|ISOLATE_TAG_HBCI|ISOLATE_TAG_HBLT|ISOLATE_TAG_hylg|ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_yccsfzjt|LN1|LN2|QA2tiepai2|beehive-scf.qhhrly.cn|eascs.beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|sny|spsi.beehive-scf.qhhrly.cn|tianma.beehive-scf.qhhrly.cn"
  - name: level
    type: number
    phys: int(10)
    desc: 层级
    topk: "1"
    labels: "1:是"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: parent_cust_id
    type: number
    phys: bigint(20)
    desc: 父企业id
    roles: [result]
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    roles: [result]
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    roles: [result]
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    roles: [result]
```

## 关联表

- [[cust_company_info]]：cust_group_rel.cust_id → cust_company_info.id（mapper:CustGroupMapper.xml，confirmed）
- [[cust_company_info]]：cust_group_rel.parent_cust_id → cust_company_info.id（java-eq:CustGroupRelApplication.java，suggested）
- [[cust_company_info]]：cust_group_rel.root_cust_id → cust_company_info.id（java-eq:CustGroupRelApplication.java，suggested）
