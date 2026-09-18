---
type: table
title: 智能审核引流卡片埋点记录
page_key: gpt_learn_poster_log
belong: tables
status: draft
anchors: [gpt_learn_poster_log]
sources: ['database_schema:lowcode_pplatform.gpt_learn_poster_log', 'code_path:GptLearnPosterLogDao.java:17']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [gpt_learn_poster_log__enable]
---

# 智能审核引流卡片埋点记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: gpt_learn_poster_log
database: lowcode_pplatform
desc: 智能审核引流卡片埋点记录
inactive: false
primary_key: [id]
grain: 学习海报弹窗记录
name_anchors: [user_name, company_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: user_id
  type: number
  desc: 用户ID
- name: user_name
  type: string
  desc: 用户名
- name: company_id
  type: number
  desc: 企业ID
- name: company_name
  type: string
  desc: 企业名称
- name: popup_time
  type: temporal
  desc: 卡片弹出时间
- name: click_time
  type: temporal
  desc: 卡片点击时间
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
default_filter:
  predicate: gpt_learn_poster_log.enable = 'Y'
  trust: confirmed
  evidence: code_path:GptLearnPosterLogDao.java:17
```

## 页面链接

### 字典

- [[dicts/gpt_learn_poster_log__enable]]（`gpt_learn_poster_log.enable`）
