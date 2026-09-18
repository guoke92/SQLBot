---
type: table
title: CFCA证书升级业务上报与触达记录
page_key: ca_cfca_upgrade_report
belong: tables
status: draft
anchors: [ca_cfca_upgrade_report]
sources: ['database_schema:lowcode_pplatform.ca_cfca_upgrade_report']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_cfca_upgrade_report__source_system, ca_cfca_upgrade_report__company_type,
  ca_cfca_upgrade_report__biz_module, ca_cfca_upgrade_report__todo_triggered, ca_cfca_upgrade_report__enable]
---

# CFCA证书升级业务上报与触达记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: ca_cfca_upgrade_report
database: lowcode_pplatform
desc: CFCA证书升级业务上报与触达记录
inactive: false
primary_key: [id]
grain: CFCA 升级上报（catalog 有表；pplatform-web 无 @TableName DO）
name_anchors: [customer_name, title, authorized_user_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: task_id
  type: string
  desc: 业务系统任务ID
- name: source_system
  type: string
  desc: 来源系统
  dict: [ACFLOW, RVSFACTOR_PC, 国内信用证, ORDER]
- name: company_id
  type: string
  desc: 企业 ID
- name: company_type
  type: string
  desc: 企业角色
  dict: [CORE, SUPPLIER, PLATFORM_COMPANY, PROJECT_COMPANY, PLATFORM_OPERATOR_COMPANY,
    FINANCE]
- name: certification_no
  type: string
  desc: 统码
- name: customer_name
  type: string
  desc: 企业/客户名称
- name: title
  type: string
  desc: 异常标题
- name: content
  type: string
  desc: 异常内容（单层 JSON）
- name: biz_module
  type: string
  desc: 所属模块
  dict: [CFCA_CA_UPGRADE, CFCA证书升级]
- name: occur_time
  type: temporal
  desc: 异常发生时间
- name: related_biz_no
  type: string
  desc: 关联业务编号
- name: trigger_scene
  type: string
  desc: 触发场景
- name: pass_info
  type: string
  desc: 透传 JSON
- name: todo_triggered
  type: string
  desc: 是否曾触发待办/消息 Y/N
  dict: [N, Y]
- name: notify_time
  type: temporal
  desc: 触发时间
- name: authorized_user_id
  type: number
  desc: 被授权人用户 ID
- name: authorized_user_name
  type: string
  desc: 被授权人姓名
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
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

- [[dicts/ca_cfca_upgrade_report__source_system]]（`ca_cfca_upgrade_report.source_system`）
- [[dicts/ca_cfca_upgrade_report__company_type]]（`ca_cfca_upgrade_report.company_type`）
- [[dicts/ca_cfca_upgrade_report__biz_module]]（`ca_cfca_upgrade_report.biz_module`）
- [[dicts/ca_cfca_upgrade_report__todo_triggered]]（`ca_cfca_upgrade_report.todo_triggered`）
- [[dicts/ca_cfca_upgrade_report__enable]]（`ca_cfca_upgrade_report.enable`）
