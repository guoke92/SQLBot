---
type: table
title: 迁移用户记录表
page_key: migratory_user_record
belong: tables
status: draft
anchors: [migratory_user_record]
sources: ['database_schema:lowcode_pplatform.migratory_user_record']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [migratory_user_record__is_login, migratory_user_record__enable]
---

# 迁移用户记录表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: migratory_user_record
database: lowcode_pplatform
desc: 迁移用户记录表
inactive: false
primary_key: [id]
grain: 用户迁移记录
name_anchors: [code, name]
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
- name: user_id
  type: number
  desc: 迁移用户id
- name: is_login
  type: string
  desc: 是否登录过
  dict: [N, Y]
- name: enable
  type: string
  desc: enable
  dict: [Y]
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

### 字典

- [[dicts/migratory_user_record__is_login]]（`migratory_user_record.is_login`）
- [[dicts/migratory_user_record__enable]]（`migratory_user_record.enable`）
