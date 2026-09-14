---
type: table
title: 客户认证配置
page_key: cust_setting_config
domain: 通知/验证码/短链
status: draft
anchors: [cust_setting_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_setting_config 保存单企业维度的开关与模板配置：既包含关键/非关键信息字段清单，也包含认证审核开关、打款验证、人脸识别，以及合同与协议类模板编码，还包含邀请码的有效期与重复发送间隔。审核类开关的判定见 [[enterprise_auth_audit_caliber]] 与 [[non_key_info_audit_caliber]]，配置开关的取值集合见 [[cust_setting_config_switch]]。

## 需求背景
企业认证与信息变更是有风险的写操作，需求侧要求企业可自行决定「认证是否需要审核」「非关键信息变更是否需要审核」，并允许开启打款验证作为认证辅助手段；邀请码则需要控制有效期与重复发送频率，防止刷取。

## 版本演进
- 审核开关、人脸识别、打款验证当前以字符串字面量 "yes"/"no" 存储，未见枚举类，取值集合见 [[cust_setting_config_switch]]。
- 邀请码有效期与重复发送间隔为「数值 + 单位」双列结构，单位由 *_unit / *_unti 列决定（sending_interval_unti 为库中实际列名拼写）。相关文档主张见 [[invitation_code_period]]。

```ground:table
table: cust_setting_config
database: lowcode_pplatform
desc: 客户认证配置
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
    topk: "CT-202404081721209495040"
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
    topk: "9999999999"
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
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
    topk: "beehive-scf.qhhrly.cn"
  - name: face_recognition
    type: string
    phys: varchar(64)
    desc: 人脸识别
    topk: "no"
  - name: invitation_code_period
    type: number
    phys: int(10)
    desc: 邀请码有效期
    topk: "1"
    labels: "1:是"
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
    topk: "yes"
  - name: need_verify_no_key
    type: string
    phys: varchar(64)
    desc: 企业非关键信息变更审核
    topk: "yes"
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
    topk: "yes"
  - name: privacy_policy_agreement
    type: string
    phys: varchar(512)
    desc: 隐私政策
    topk: "CT-202404031807156758507"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sending_interval
    type: number
    phys: int(10)
    desc: 邀请码重复发送时间间隔
    topk: "1"
    labels: "1:是"
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
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: user_agreement
    type: string
    phys: varchar(512)
    desc: 用户协议
    topk: "CT-202404031806394575219"
```