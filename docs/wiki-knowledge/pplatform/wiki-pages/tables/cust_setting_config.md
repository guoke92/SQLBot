---
type: table
title: 客户认证配置
page_key: cust_setting_config
belong: tables
domain: 基线
status: draft
anchors: [cust_setting_config]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户认证配置

（基线页：36 字段，行数估计 0。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_setting_config
database: lowcode_pplatform
desc: 客户认证配置
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
  - name: authorization_change
    type: string
    phys: varchar(512)
    desc: 数字证书服务协议
  - name: authorization_offline
    type: string
    phys: varchar(512)
    desc: 授权确认书-线下签署
  - name: authorization_online
    type: string
    phys: varchar(512)
    desc: 授权确认书-线上签署
  - name: cfca_agreement
    type: string
    phys: varchar(512)
    desc: 数字证书服务协议
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
  - name: face_recognition
    type: string
    phys: varchar(64)
    desc: 人脸识别
  - name: invitation_code_period
    type: number
    phys: int(10)
    desc: 邀请码有效期
  - name: invitation_code_period_unit
    type: string
    phys: varchar(64)
    desc: 邀请码有效期单位
  - name: key_word
    type: string
    phys: varchar(1024)
    desc: 企业关键信息
  - name: name
    type: string
    phys: varchar(128)
    desc: 配置名称
  - name: need_auth_verify
    type: string
    phys: varchar(64)
    desc: 企业认证审核
  - name: need_verify_no_key
    type: string
    phys: varchar(64)
    desc: 企业非关键信息变更审核
  - name: no_key_word
    type: string
    phys: varchar(1024)
    desc: 企业非关键信息配置
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: payment_maximum_number
    type: number
    phys: int(10)
    desc: 最多申请打款次数
  - name: payment_verification
    type: string
    phys: varchar(64)
    desc: 打款验证
  - name: privacy_policy_agreement
    type: string
    phys: varchar(512)
    desc: 隐私政策
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sending_interval
    type: number
    phys: int(10)
    desc: 邀请码重复发送时间间隔
  - name: sending_interval_unti
    type: string
    phys: varchar(64)
    desc: 邀请码重复发送时间间隔单位
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: user_agreement
    type: string
    phys: varchar(512)
    desc: 用户协议
```
