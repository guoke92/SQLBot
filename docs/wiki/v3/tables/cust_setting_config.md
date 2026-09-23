---
type: table
title: 客户认证配置
page_key: cust_setting_config
belong: tables
status: draft
anchors:
- cust_setting_config
sources:
- database_schema:lowcode_pplatform.cust_setting_config
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_account_info
- cust_setting_config__enable
---
# 客户认证配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_setting_config
database: lowcode_pplatform
desc: 客户认证配置
inactive: false
primary_key:
- id
grain: 租户级建档配置，运行时 list().get(0) 取第一条，不是按企业 id 查
name_anchors:
- code
- name
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
  desc: 配置名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label: [启用, 停用]
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
- name: key_word
  type: string
  desc: 企业关键信息
- name: need_verify_no_key
  type: string
  desc: 企业非关键信息变更审核
- name: user_agreement
  type: string
  desc: 用户协议
- name: privacy_policy_agreement
  type: string
  desc: 隐私政策
- name: authorization_online
  type: string
  desc: 授权确认书-线上签署
- name: authorization_offline
  type: string
  desc: 授权确认书-线下签署
- name: authorization_change
  type: string
  desc: 数字证书服务协议
- name: cfca_agreement
  type: string
  desc: 数字证书服务协议
- name: need_auth_verify
  type: string
  desc: 企业认证审核
- name: face_recognition
  type: string
  desc: 人脸识别
- name: payment_verification
  type: string
  desc: 打款验证
- name: payment_maximum_number
  type: number
  desc: 最多申请打款次数
- name: no_key_word
  type: string
  desc: 企业非关键信息配置
- name: invitation_code_period
  type: number
  desc: 邀请码有效期
- name: invitation_code_period_unit
  type: string
  desc: 邀请码有效期单位
- name: sending_interval
  type: number
  desc: 邀请码重复发送时间间隔
- name: sending_interval_unti
  type: string
  desc: 邀请码重复发送时间间隔单位
- name: cust_id
  type: number
  desc: 企业id
```

## 关联关系

_（本页暂无保留的 EQUI_JOIN 边；已移除边见 `_raw/join_validation/removed_relations.md`。）_


## 关联说明（非 EQUI / 对等场景）

- **非 EQUI 依赖**：全局配置；`payment_maximum_number` 在打款次数初始化时**赋值拷贝**到 `cust_account_info.payment_remaining_count`（`updatePayCount`），不是表间外键 / 等值 JOIN。
- 勿因「被账户使用」而强行挂 EQUI_JOIN。

## 页面链接

### 关联表

- [[tables/cust_account_info]]

### 字典

- [[dicts/cust_setting_config__enable]]（`cust_setting_config.enable`）
