---
type: table
title: cust_message_send_policy 消息发送策略表
page_key: table/cust_message_send_policy
domain: 通知/验证码/短链
status: draft
aliases: [消息发送策略, 消息策略表, custMessageSendPolicy]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_message_send_policy
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---


cust_message_send_policy 是通知链路的场景开关表：一行代表「某场景 × 某渠道」是否实际发送。`scenes_type` 是定位消息模板与场景实现类的主键式入口，与代码中的 SmsTemplateConstant / NoticeTemplateConstant / EmailTemplateConstansts 常量值对齐；`msg_kind` 区分短信/邮件/站内信等渠道维度；`send_enable` 是最终是否发出的闸门。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版，无历史版本记录。`send_enable` 默认 Y。

```ground:table
table: cust_message_send_policy
database: lowcode_pplatform
desc: 客户消息发送策略
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
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: msg_kind
    type: string
    desc: 消息类型
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: remark
    type: string
    desc: remark
  - name: scenes_type
    type: string
    desc: 场景码
  - name: send_enable
    type: string
    desc: 发送标识
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

## 关联

[[concepts/场景码]] · [[concepts/站内信]] · [[processes/消息渠道]] · [[calibers/短信发送默认参数]] · [[calibers/消息模板缺失]] · [[rules/通知发送失败不阻断主流程]] · [[rules/前置校验异常不受静默策略保护]]