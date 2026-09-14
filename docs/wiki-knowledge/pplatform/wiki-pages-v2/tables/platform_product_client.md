---
type: table
title: 平台产品端口配置
page_key: platform_product_client
domain: 平台产品配置
status: draft
anchors: [platform_product_client]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---
















platform_product_client 描述平台产品在不同客户端上的接入配置。一个产品可以对应多种客户端类型与多种链接方式，链接类型（iframe/redirect/forward）决定产品入口的跳转方式，`ext_config` 承载各客户端差异化的扩展配置，`multiple_type` 用于按类型做过滤。

本表与 [[tables/platform_product]] 是配置与接入的关系：产品定义决定「能不能用」，客户端配置决定「从哪儿、以什么方式进入」。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景暂不展开需求文档层面的叙述，仅按库表结构整理字段含义。

## 版本演进

v0 契约首次建档，4 个字段语义均来自库表结构证据。

```ground:table
table: platform_product_client
database: lowcode_pplatform
desc: 平台产品端口配置
fields:
  - name: client_type
    type: string
    phys: varchar(32)
    desc: 客户端类型方式
    dict: platform_product_client__client_type
    topk: "ACFLOW|AMS|BEECREDIT|DEALER|ORDER|RVSFACTOR_PC"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: link_type
    type: string
    phys: varchar(16)
    desc: 链接类型(iframe/redirect/forward)
    dict: link_type
    topk: "iframe"
  - name: multiple_type
    type: string
    phys: varchar(128)
    desc: 过滤类型
    dict: multiple_type
    topk: "CORE|CORE_BRANCH|CORE_MANAGER|CORE_SUB|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|default"
  - name: status
    type: string
    phys: varchar(512)
    desc: 启用状态
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: wx_flag
    type: string
    phys: varchar(512)
    desc: 是否小程序
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
    topk: "beehive-scf.qhhrly.cn"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
  - name: ext_config
    type: string
    phys: varchar(1024)
    desc: 其他配置信息
  - name: name
    type: string
    phys: varchar(128)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: 平台产品id
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
  - name: url
    type: string
    phys: varchar(1024)
    desc: 产品url
```

## 关联

- 产品主表：[[tables/platform_product]]
- 产品编码语义：[[concepts/productCode]]
- 产品列表过滤：[[rules/platform-product-list-filter]]