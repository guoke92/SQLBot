---
type: table
title: cust_setting_config 企业配置表
page_key: table/cust_setting_config
domain: 通知/验证码/短链
status: draft
aliases: [企业配置, 租户配置表, custSettingConfig]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_setting_config
contract_version: "0.1"
---


cust_setting_config 按企业（`cust_id`）保存认证与邀请类业务的可配置项：哪些字段算关键信息、变更是否需要审核、认证是否走人脸或打款验证、以及一组协议模板编号。它以配置驱动代替硬编码，本主题相关的主要是邀请码有效期与发送间隔这两个窗口参数。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版，无历史版本记录。

```ground:table
table: cust_setting_config
database: lowcode_pplatform
desc: 客户认证配置
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: authorization_change
    type: string
    desc: 数字证书服务协议
  - name: authorization_offline
    type: string
    desc: 授权确认书-线下签署
  - name: authorization_online
    type: string
    desc: 授权确认书-线上签署
  - name: cfca_agreement
    type: string
    desc: 数字证书服务协议
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: cust_id
    type: number
    desc: 企业id
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: face_recognition
    type: string
    desc: 人脸识别
  - name: invitation_code_period
    type: number
    desc: 邀请码有效期
  - name: invitation_code_period_unit
    type: string
    desc: 邀请码有效期单位
  - name: key_word
    type: string
    desc: 企业关键信息
  - name: name
    type: string
    desc: 配置名称
  - name: need_auth_verify
    type: string
    desc: 企业认证审核
  - name: need_verify_no_key
    type: string
    desc: 企业非关键信息变更审核
  - name: no_key_word
    type: string
    desc: 企业非关键信息配置
  - name: organization_id
    type: string
    desc: 机构编号
  - name: payment_maximum_number
    type: number
    desc: 最多申请打款次数
  - name: payment_verification
    type: string
    desc: 打款验证
  - name: privacy_policy_agreement
    type: string
    desc: 隐私政策
  - name: remark
    type: string
    desc: remark
  - name: sending_interval
    type: number
    desc: 邀请码重复发送时间间隔
  - name: sending_interval_unti
    type: string
    desc: 邀请码重复发送时间间隔单位
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
  - name: user_agreement
    type: string
    desc: 用户协议
```

## 关联

[[calibers/邀请码有效期]] · [[concepts/验证码]]