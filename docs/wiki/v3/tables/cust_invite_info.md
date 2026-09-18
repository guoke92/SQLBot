---
type: table
title: 客户邀请信息
page_key: cust_invite_info
belong: tables
status: draft
anchors: [cust_invite_info]
sources: ['database_schema:lowcode_pplatform.cust_invite_info']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_invite_info__progress, cust_invite_info__enable]
---

# 客户邀请信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_invite_info
database: lowcode_pplatform
desc: 客户邀请信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, contact_name, channel_code]
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
- name: progress
  type: string
  desc: 进度
  dict: [INIT, CUST_CONFIRM_AWAIT, BUILD_SUCCESS, CUST_BUILDING, CUST_CHANGE, BUILD_FAIL,
    AWAIT_CUST_CONFIRM, BUILDING]
  label: [初始化, 待客户认证, 认证成功, 审核中, 变更, 认证失败, 待客户确认, 建档中]
- name: invite_time
  type: temporal
  desc: 邀请时间
- name: contact_name
  type: string
  desc: 联系人
- name: email
  type: string
  desc: 邮箱
- name: contact_phone
  type: string
  desc: 联系人手机号码
- name: channel_code
  type: string
  desc: 渠道码
- name: invite_from
  type: string
  desc: 邀请主体
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
- name: invite_cust_id
  type: number
  desc: 邀请客户id
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_invite_info.invite_cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyIfoEnchanceService.java:1587
source: l1_code
join_role: identity
priority: primary
authenticity_note: 邀请方企业主键。progress 回写按被邀请企业 name+db_tenant_code 匹配，不是这条 JOIN。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_invite_info__progress]]（`cust_invite_info.progress`）
- [[dicts/cust_invite_info__enable]]（`cust_invite_info.enable`）
