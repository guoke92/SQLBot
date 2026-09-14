---
type: table
title: 客户消息发送策略
page_key: cust_message_send_policy
domain: 通知/验证码/短链
status: draft
anchors: [cust_message_send_policy]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_message_send_policy 以「消息类型 + 场景码」为粒度控制企业侧消息是否发送，是通知组件在客户域的开关表。发送开关默认 Y，并另有启用标识 enable 控制记录本身是否生效。

## 需求背景
通知触达需要按企业的业务场景做精细化开关（例如某企业不希望收到某类短信），因此需要按 msg_kind 与 scenes_type 组合配置发送策略，避免在代码中硬编码场景。

## 版本演进
- 当前该表只有配置语义，未见与验证码/短链链路的直接关联证据，相关通知发送规则见 [[verify_code_scenes_whitelist]] 与 [[notice_local_downstream_route]]。

```ground:table
table: cust_message_send_policy
database: lowcode_pplatform
desc: 客户消息发送策略
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
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
  - name: msg_kind
    type: string
    phys: varchar(60)
    desc: 消息类型
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: scenes_type
    type: string
    phys: varchar(60)
    desc: 场景码
  - name: send_enable
    type: string
    phys: varchar(2)
    desc: 发送标识
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
```