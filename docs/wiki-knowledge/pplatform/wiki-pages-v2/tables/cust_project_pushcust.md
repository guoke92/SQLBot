---
type: table
title: 推送企业的默认项目
page_key: cust_project_pushcust
domain: 项目报表/统计/上报
status: draft
anchors: [cust_project_pushcust]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_project_pushcust 描述从一个系统跳转到另一个系统时所使用的 SSO 渠道配置，字段以「起始系统」与「跳转系统」两侧成对出现，供免登跳转链路读取。它是项目报表/统计主题中唯一与 SSO 渠道相关的落库表，因此需求文档中关于登录改造的主张被挂在[[concepts/project_ledger|项目台账]]之外的此处做边界澄清。

## 需求背景

本次语义分析中，本表仅有 DB 证据（字段语义），无代码路径证据；SSO 渠道的具体取值集合未在分析中给出，契约不发明字典值。

## 版本演进

v0 契约首版，仅登记两个渠道字段。需求文档中「SSO 验证码登录改造」相关主张经判定与本主题（项目报表/统计/上报）无关，未证实，见下方 REVIEW。

```ground:table
table: cust_project_pushcust
database: lowcode_pplatform
desc: 推送企业的默认项目
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
    topk: "ISOLATE_TAG_HBLT|ISOLATE_TAG_JHYL|ZTSJ"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: string
    phys: varchar(64)
    desc: 项目id
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_sso_channel
    type: string
    phys: varchar(100)
    desc: 起始系统的SSO渠道
    topk: "JHYL|ZTSJ|dahua|hubeiliantou"
  - name: target_sso_channel
    type: string
    phys: varchar(100)
    desc: 跳转系统的SSO渠道
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

---REVIEW: table | 客户项目推送客户SSO渠道表---
需求文档主张「SSO 验证码登录改造」与项目报表/统计/上报主题无关（code_status=uncovered，action=review）。当前无代码证据可判断该主张与 cust_project_pushcust 的 source_sso_channel/target_sso_channel 是否存在隐性耦合：本表两个渠道字段的取值域、由谁写入、是否受登录改造影响均未确认。需业务方与代码 owner 确认后再决定是否将本表纳入本主题契约或移出至登录域。
---END REVIEW---