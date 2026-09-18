---
type: table
title: 机构管理
page_key: org_manage
belong: tables
status: draft
anchors: [org_manage]
sources: ['database_schema:lowcode_pplatform.org_manage']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
---

# 机构管理

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: org_manage
database: lowcode_pplatform
desc: 机构管理
inactive: false
primary_key: [id]
grain: 组织
name_anchors: [code, name, org_name, parent_code]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: org_no
  type: string
  desc: 机构号
- name: org_name
  type: string
  desc: 机构名称
- name: org_level
  type: number
  desc: 机构层级
- name: org_type
  type: string
  desc: 机构类型
- name: status
  type: string
  desc: 状态
- name: client_type
  type: string
  desc: 端类型
- name: parent_code
  type: string
  desc: 父机构编号
- name: enable
  type: string
  desc: enable
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
```

## 页面链接

- [[concepts/catalog_summary]]
