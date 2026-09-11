---
type: table
title: 运营人员表 operation_user
page_key: table.operation_user
domain: 数据权限与组织
status: draft
aliases: [operation_user, 运营中台人员表, 运营人员]
oid: 1
scope:
  databases: [base]
sources: [db]
contract_version: "0.1"
---


运营中台侧的运营人员主数据表，保存运营人员的业务编码、姓名、运营组别、所属机构编号以及审批流实例信息。本表是「运营人员归属」的源端：产融侧 [[tables/cust_person_info]] 的 operator_id / operator_realname / operator 三个字段分别冗余自本表的 operation_id / operation_name 与登录名，构成 [[concepts/operator_identity_bridge]]。本表 organization_id 与 [[tables/org_manage]] 同域，构成 [[concepts/org_identity_bridge]]。

本表的审计字段（create_by / create_user / update_by / update_user）实测全部为空串，说明审计值实际未落值，排障时不可将其作为「谁创建了运营人员」的依据。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；现有结论均来自物理库字段语义（db 证据）。

## 版本演进

v0：依据 db 证据建档。其中 enable / deleted / db_tenant_code 附有实测分布，是查询口径的直接依据，删除过滤规则见 [[rules/operation_user_deleted_filter]]。

```ground:table
table: operation_user
database: lowcode_pplatform
desc: 运营中台人员数据
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: deleted
    type: string
    desc: 删除标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: operation_group
    type: string
    desc: 运营组别
  - name: operation_id
    type: string
    desc: 运营中台id
  - name: operation_name
    type: string
    desc: 运营人员姓名
  - name: organization_id
    type: string
    desc: 机构编号
  - name: remark
    type: string
    desc: remark
  - name: status
    type: string
    desc: 用户状态标识
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```