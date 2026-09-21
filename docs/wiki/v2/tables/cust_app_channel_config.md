---
type: table
title: 客户应用渠道关系
page_key: cust_app_channel_config
belong: tables
status: draft
anchors: [cust_app_channel_config]
sources: ['database_schema:lowcode_pplatform.cust_app_channel_config']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_app_channel_config__app_id, cust_app_channel_config__code, cust_app_channel_config__name,
  cust_app_channel_config__enable]
---

# 客户应用渠道关系

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_app_channel_config
database: lowcode_pplatform
desc: 客户应用渠道关系
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: app_id
  type: string
  desc: 应用id
  dict: [73d62771729e4ffba7f263cb6012746d, d547c3081b1a44d7992031434438e1f3]
- name: code
  type: string
  desc: 编码
  dict: [longteng, jingke]
- name: name
  type: string
  desc: 名称
  dict: [longteng, jingke]
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

- [[dicts/cust_app_channel_config__app_id]]（`cust_app_channel_config.app_id`）
- [[dicts/cust_app_channel_config__code]]（`cust_app_channel_config.code`）
- [[dicts/cust_app_channel_config__name]]（`cust_app_channel_config.name`）
- [[dicts/cust_app_channel_config__enable]]（`cust_app_channel_config.enable`）
