---
type: table
title: short_link 短链表
page_key: table/short_link
domain: 通知/验证码/短链
status: draft
aliases: [短链, 短链表, shortLink, short_link]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:short_link
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
contract_version: "0.1"
---


short_link 是短链跳转链路的唯一数据源：一行代表一条可访问短链，业务访问键是 `number`，跳转目标是 `source_url`。`type` 决定跳转前是否需要用 `fileService.filePathEncrypt` 换链，`is_forever` / `expire_time` 决定是否放行，`enable` 与 `db_tenant_code` 提供逻辑有效性与租户维度的过滤面。表内 `code` 属框架级通用编码字段，与业务访问口径不是同一件事，勿与 `number` 混用。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定，业务定位完全来自代码与 DB 实测。

## 版本演进

v0 首版。DB 实测存量（type：FILE=605 / NORMAL=4750；is_forever 全为 Y 共 5355 条；db_tenant_code 仅 base 一个租户）是当前数据现状快照，不是版本变更记录。

```ground:table
table: short_link
database: lowcode_pplatform
desc: 短链接
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
  - name: expire_time
    type: temporal
    desc: 到期时间
  - name: is_forever
    type: string
    desc: 到期类型
  - name: name
    type: string
    desc: 名称
  - name: number
    type: string
    desc: 编码
  - name: organization_id
    type: string
    desc: 机构编号
  - name: remark
    type: string
    desc: remark
  - name: source_url
    type: string
    desc: 源链接
  - name: type
    type: string
    desc: 类型
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

[[concepts/短链]] · [[processes/短链类型路由]] · [[processes/短链有效期标志]] · [[calibers/短链已过期]] · [[calibers/永久短链]] · [[calibers/普通短链]] · [[calibers/文件短链]]