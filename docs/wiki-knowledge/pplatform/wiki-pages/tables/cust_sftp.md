---
type: table
title: 客戶sftp信息
page_key: cust_sftp
belong: tables
domain: 基线
status: draft
anchors: [cust_sftp]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客戶sftp信息

（基线页：25 字段，行数估计 13。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_sftp
database: lowcode_pplatform
desc: 客戶sftp信息
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
  - name: channel
    type: string
    phys: varchar(64)
    desc: 渠道
    topk: ZTSJ|alipayAnt|alipayAnt-test|app_bosc_shtl
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_zjsj|ZTSJ
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: host
    type: string
    phys: varchar(64)
    desc: 服务器地址IP地址
    topk: qa.sftp.lls.com|uat.sftp.lls.com
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: 中铁四局|创维-SAP|天合光能|怡亚通
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: password
    type: string
    phys: varchar(64)
    desc: 登录密码
  - name: port
    type: number
    phys: int(10)
    desc: 端口
    topk: 22
  - name: private_key
    type: string
    phys: varchar(64)
    desc: 私钥
  - name: private_key_pwd
    type: string
    phys: varchar(256)
    desc: 私钥的密码
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
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: user_name
    type: string
    phys: varchar(64)
    desc: 登录用户名
    topk: app_JingKeNengY926_20240614|app_alipayAnt_202606301619|app_bgy_20250306|app_bosc_shtl
```
