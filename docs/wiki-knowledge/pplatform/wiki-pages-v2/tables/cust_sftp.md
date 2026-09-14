---
type: table
title: 客戶sftp信息
page_key: cust_sftp
domain: 企业银行账户/集团/SFTP
status: draft
anchors: [cust_sftp]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_sftp 保存渠道影像文件传输通道的连接配置，按 channel + enable 联查，用于影像下载/回传。

## 需求背景
非自主建档强制要求提交营业执照、法人证件、经办人证件与授权书影像（见 [[independent_archive_validation]]），影像落地依赖本表通道；通道匹配不到时按 [[sftp_channel_enable]] 直接抛 SERVER_BUSY。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_sftp
database: lowcode_pplatform
desc: 客戶sftp信息
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
  - name: channel
    type: string
    phys: varchar(64)
    desc: 渠道
    topk: "ZTSJ|alipayAnt|alipayAnt-test|app_bosc_shtl|app_jkny|bgy|dahua|dahua-test|eascs|hbjg|longteng|meituan|sny|sny_test|tianma|trinasolar"
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
    topk: "ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_zjsj|ZTSJ|beehive-scf.qhhrly.cn|eascs.beehive-scf.qhhrly.cn|jkny|minmetals|sny|tianma.beehive-scf.qhhrly.cn|xylxchf"
  - name: host
    type: string
    phys: varchar(64)
    desc: 服务器地址IP地址
    topk: "qa.sftp.lls.com|uat.sftp.lls.com"
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
    desc: 登录密码
  - name: port
    type: number
    phys: int(10)
    desc: 端口
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
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: user_name
    type: string
    phys: varchar(64)
    desc: 登录用户名
    topk: "app_JingKeNengY926_20240614|app_LongTengYC_609152804|app_alipayAnt_202606301619|app_bgy_20250306|app_bosc_shtl|app_cclocal_601636163|app_dahua2026041601|app_eascs_2022070823|app_ofhbjg_20260409|app_sny_202607235624|app_trinasolar_2023051522|app_ztsj_2026033169|meituan"
```
