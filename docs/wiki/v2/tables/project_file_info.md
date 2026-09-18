---
type: table
title: 项目运营文件管理
page_key: project_file_info
belong: tables
status: draft
anchors: [project_file_info]
sources: ['database_schema:lowcode_pplatform.project_file_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [project_file_info__file_type, project_file_info__enable]
---

# 项目运营文件管理

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### file_content

`title`, `content`, `file_type`

### relation

`project_id`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: project_file_info
database: lowcode_pplatform
description: 项目运营文件管理
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [title, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计
  trust: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: file_content
  title: 文件内容
  trust: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: relation
  title: 项目机构关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: title
  data_type: string
  description: 标题
  cluster: file_content
- name: content
  data_type: string
  description: 描述
  cluster: file_content
- name: file_type
  data_type: string
  description: 文件模块类型
  cluster: file_content
  dictionary: project_file_info__file_type
- name: project_id
  data_type: number
  description: 关联项目ID
  cluster: relation
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: project_file_info__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: relation
```

## 页面链接

### 字典

- [[dicts/project_file_info__file_type]]（`project_file_info.file_type`）
- [[dicts/project_file_info__enable]]（`project_file_info.enable`）
