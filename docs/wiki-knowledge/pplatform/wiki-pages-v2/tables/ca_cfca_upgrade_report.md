---
type: table
title: ca_cfca_upgrade_report
page_key: table/ca_cfca_upgrade_report
domain: CA证书认证
status: draft
aliases: [CFCA证书升级异常上报表]
oid: 1
scope:
  databases: [unknown]
sources: [db]
contract_version: "0.1"
---


ca_cfca_upgrade_report 记录 CFCA 证书升级过程中的异常上报信息：哪一类模块（biz_module）、来自哪个来源系统（source_system）、标题是什么（title）、对应企业与统一社会信用代码（company_id、certification_no）、被授权人（authorized_user_name）、是否曾触发待办/消息（todo_triggered），以及异常内容与透传报文（content、pass_info）。

该表是升级链路的观测面：当签章中台证书登记名与运营中台企业名不一致时，需要走在线盖章的升级授权书流程（[[rules/upgrade_auth_online_seal]]）；证书状态被归一化为 CANCELLED/EXPIRED/FAIL 或名称不匹配时会回写企业侧标识（[[rules/ca_invalidate_writeback]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。本页字段语义全部来自库结构证据（db），biz_module、source_system、title 的取值体现了同一升级事件的多种书写形态（例如 CFCA_CA_UPGRADE 与「CFCA证书升级」），与 [[concepts/ca]] 的术语归属相关但不能等同于证书本身的状态。

## 版本演进

暂无文档化的版本演进证据。可作为后续核对的锚点是 todo_triggered 字段：它记录该异常是否曾触发待办或消息，但本页不推断其触发时机与触发条件。

```ground:table
table: ca_cfca_upgrade_report
database: lowcode_pplatform
desc: CFCA证书升级业务上报与触达记录
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
  - name: authorized_user_id
    type: number
    desc: 被授权人用户 ID
  - name: authorized_user_name
    type: string
    desc: 被授权人姓名
  - name: biz_module
    type: string
    desc: 所属模块
  - name: certification_no
    type: string
    desc: 统码
  - name: code
    type: string
    desc: 编码
  - name: company_id
    type: string
    desc: 企业 ID
  - name: company_type
    type: string
    desc: 企业角色
  - name: content
    type: string
    desc: 异常内容（单层 JSON）
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: customer_name
    type: string
    desc: 企业/客户名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: notify_time
    type: temporal
    desc: 触发时间
  - name: occur_time
    type: temporal
    desc: 异常发生时间
  - name: organization_id
    type: string
    desc: 机构编号
  - name: pass_info
    type: string
    desc: 透传 JSON
  - name: related_biz_no
    type: string
    desc: 关联业务编号
  - name: remark
    type: string
    desc: remark
  - name: source_system
    type: string
    desc: 来源系统
  - name: task_id
    type: string
    desc: 业务系统任务ID
  - name: title
    type: string
    desc: 异常标题
  - name: todo_triggered
    type: string
    desc: 是否曾触发待办/消息 Y/N
  - name: trigger_scene
    type: string
    desc: 触发场景
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

相关页面：[[tables/ca_certification_info]]、[[rules/upgrade_auth_online_seal]]。