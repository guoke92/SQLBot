---
type: table
title: 客户接入秘钥信息
page_key: cust_access_secret
domain: 准入接入与接入密钥
status: draft
anchors: [cust_access_secret]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_access_secret 保存外部渠道的接入秘钥与租户映射，是「渠道 → 数据租户」定位与渠道鉴权的唯一依据（见 [[channel]]、[[tenant]]）。

## 需求背景
渠道入站请求先以 `all` 租户检索（[[inbound_all_tenant_context]]），再由本表的 channel + enable 联查反查真实 dbTenantCode；渠道未启用或匹配不到时按 [[channel_enable_filter]] 直接拒绝。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_access_secret
database: lowcode_pplatform
desc: 客户接入秘钥信息
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: encry_type
    type: string
    phys: varchar(64)
    desc: 加密类型
    dict: encry_type
    topk: "rsa"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: status_query_license_enabled
    type: string
    phys: varchar(4)
    desc: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
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
  - name: channel
    type: string
    phys: varchar(64)
    desc: 应用id
    topk: "ZTSJ|alipayAnt|alipayAnt-test|app_bosc_shtl|app_jkny|bgy|dahua|dahua-test|eascs|hbjg|lls|longteng|meituan|sny|sny_test|tianma|trinapower|trinasolar|yhkj"
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
    topk: "ISOLATE_TAG_YINHEKEJI|ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_zjsj|ZTSJ|beehive-scf.qhhrly.cn|eascs.beehive-scf.qhhrly.cn|jkny|minmetals|sny|tianma.beehive-scf.qhhrly.cn|xylxchf"
  - name: key_num
    type: number
    phys: int(11)
    desc: 密钥对
    topk: "2"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: password
    type: string
    phys: varchar(64)
    desc: 密码
  - name: pri_key
    type: string
    phys: varchar(256)
    desc: 私钥
  - name: pub_key
    type: string
    phys: varchar(256)
    desc: 公钥
  - name: rel_lls_secret_id
    type: number
    phys: bigint(22)
    desc: 关联平台密钥记录id
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
```