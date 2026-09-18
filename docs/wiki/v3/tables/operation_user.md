---
type: table
title: 运营中台人员数据
page_key: operation_user
belong: tables
status: draft
anchors: [operation_user]
sources: ['database_schema:lowcode_pplatform.operation_user', 'code_path:OperCustFacade.java:4166']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [operation_user__deleted, operation_user__enable]
---

# 运营中台人员数据

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: operation_user
database: lowcode_pplatform
desc: 运营中台人员数据
inactive: false
primary_key: [id]
grain: 运营人员
name_anchors: [operation_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: operation_id
  type: string
  desc: 运营中台id
- name: status
  type: string
  desc: 用户状态标识
- name: operation_group
  type: string
  desc: 运营组别
- name: deleted
  type: string
  desc: 删除标识
  dict: [N, Y]
- name: operation_name
  type: string
  desc: 运营人员姓名
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
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
default_filter:
  predicate: operation_user.enable = 'Y'
  trust: confirmed
  evidence: code_path:OperCustFacade.java:4166
```

## 页面链接

### 字典

- [[dicts/operation_user__deleted]]（`operation_user.deleted`）
- [[dicts/operation_user__enable]]（`operation_user.enable`）
