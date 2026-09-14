---
type: table
title: 短链接
page_key: short_link
domain: 通知/验证码/短链
status: draft
anchors: [short_link]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












short_link 是平台短链服务的核心存储表，承载短链码（number）、短链类型（type）、跳转目标（source_url）与有效期策略（is_forever / expire_time），并带有数据租户与逻辑租户隔离字段。访问侧由 [[short_link_type_route]] 决定跳转方式，由 [[short_link_expire_check]] 决定是否拦截过期链接，由 [[short_link_id_verify_code]] 防止短链被枚举。

短链在语义上先按有效期分为 [[permanent_short_link]] 与 [[temporary_short_link]]（见 [[short_link_expire_state]]），再按类型分为 [[normal_short_link]] 与 [[file_short_link]]，两条切分维度互相独立。

## 需求背景
短链服务面向通知与客户触达场景提供可对外投放的短链接，因此需要区分「永久有效」与「限时有效」两种投放策略，并对文件类目标链接隐藏真实路径。需求侧要求短链不可被顺序枚举，故在短链码中内嵌校验位。

## 版本演进
- 当前 DB 中 is_forever 全部为 "Y"，未见 "N" 样本；限时分支的行为依据代码常量与 [[temporary_short_link_expire_check]]。
- 需求文档提出「需要短链时由 ShortLinkAppication 生成短链」，代码链路中仅见访问侧 ShortLinkController，生成侧未被证实，见 REVIEW。

```ground:table
table: short_link
database: lowcode_pplatform
desc: 短链接
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
  - name: is_forever
    type: string
    phys: varchar(64)
    desc: 到期类型
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: type
    type: string
    phys: varchar(64)
    desc: 类型
    dict: short_link__type
    topk: "FILE|NORMAL"
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
    topk: "base"
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
  - name: expire_time
    type: temporal
    phys: datetime
    desc: 到期时间
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: number
    type: string
    phys: varchar(64)
    desc: 编码
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_url
    type: string
    phys: varchar(2048)
    desc: 源链接
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