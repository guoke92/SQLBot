---
type: table
title: CFCA证书升级业务上报与触达记录
page_key: ca_cfca_upgrade_report
domain: 基线
status: draft
anchors: [ca_cfca_upgrade_report]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# CFCA证书升级业务上报与触达记录

（基线页：35 字段，行数估计 385。行语义/常用过滤待语义摄取增强。）

```ground:table
table: ca_cfca_upgrade_report
database: lowcode_pplatform
desc: CFCA证书升级业务上报与触达记录
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
  - name: authorized_user_id
    type: number
    phys: bigint(20)
    desc: 被授权人用户 ID
  - name: authorized_user_name
    type: string
    phys: varchar(512)
    desc: 被授权人姓名
    topk: 何云|佘雨代|利胜健|吴志勇
  - name: biz_module
    type: string
    phys: varchar(128)
    desc: 所属模块
    topk: CFCA_CA_UPGRADE|CFCA证书升级
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: string
    phys: varchar(128)
    desc: 企业 ID
  - name: company_type
    type: string
    phys: varchar(128)
    desc: 企业角色
    topk: CORE|FINANCE|PLATFORM_COMPANY|PLATFORM_OPERATOR_COMPANY
  - name: content
    type: string
    phys: text
    desc: 异常内容（单层 JSON）
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
  - name: customer_name
    type: string
    phys: varchar(512)
    desc: 企业/客户名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: LN1|beehive-scf.qhhrly.cn|sdhsg.beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: notify_time
    type: temporal
    phys: datetime
    desc: 触发时间
  - name: occur_time
    type: temporal
    phys: datetime
    desc: 异常发生时间
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pass_info
    type: string
    phys: text
    desc: 透传 JSON
  - name: related_biz_no
    type: string
    phys: varchar(128)
    desc: 关联业务编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_system
    type: string
    phys: varchar(128)
    desc: 来源系统
    topk: ACFLOW|ORDER|RVSFACTOR_PC|国内信用证
  - name: task_id
    type: string
    phys: varchar(64)
    desc: 业务系统任务ID
  - name: title
    type: string
    phys: varchar(512)
    desc: 异常标题
    topk: CFCA证书升级
  - name: todo_triggered
    type: string
    phys: varchar(2)
    desc: 是否曾触发待办/消息 Y/N
    topk: N|Y
  - name: trigger_scene
    type: string
    phys: varchar(128)
    desc: 触发场景
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
```
