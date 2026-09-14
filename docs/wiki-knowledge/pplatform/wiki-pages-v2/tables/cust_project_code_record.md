---
type: table
title: 企业项目码输入记录
page_key: cust_project_code_record
domain: 项目报表/统计/上报
status: draft
anchors: [cust_project_code_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_project_code_record 记录企业/项目编码类数据的写入与校验结果，type 区分产生记录的场景（如 userCompanyRegister、产品中心等），status 表示该次编码是否正确。它与[[tables/cust_project_rel|cust_project_rel]]通过 company_id 关联企业主数据（FK，confirm，CustProjectRelEnhanceService.java）。

## 需求背景

本表在本次分析中只有 DB 证据，未出现需求文档主张；字段语义以 DB 值为准。

## 版本演进

v0 契约首版。status 的 DB 实际取值域为 Y/N，与代码枚举 StatusEnum.EFFECTIVE/INVALID 的存储值不一致（enum_audit verdict=reject），详见 [[enums/cust_project_code_record_status|cust_project_code_record.status 值点]]。

```ground:table
table: cust_project_code_record
database: lowcode_pplatform
desc: 企业项目码输入记录
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
  - name: status
    type: string
    phys: varchar(4)
    desc: 是否正确状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: type
    type: string
    phys: varchar(32)
    desc: 类型
    dict: cust_project_code_record__type
    topk: "PC_BUILD|userCompanyRegister|产品中心|产品中心-企业认证成功"
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
    topk: "base|common|xyc.llschain.com"
  - name: channel_code
    type: string
    phys: varchar(32)
    desc: 渠道码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: company_type
    type: string
    phys: varchar(200)
    desc: 企业角色
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
    topk: "HKC|ISOLATE_TAG_HBCI|ISOLATE_TAG_LONGYANCHENGFA|ISOLATE_TAG_NAURA|ISOLATE_TAG_lygs|ISOLATE_TAG_yccsfzjt|ISOLATE_TAG_ytzl|JFT|LN1|beehive-scf.qhhrly.cn|cdpd|dhhk|jiuersanzuhu|jkny|lho2zuhu2|ning|spsi.beehive-scf.qhhrly.cn|wukong|zhongtieqijujituanyouxiangongsi|zuhuyanshi01"
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
  - name: use_id
    type: number
    phys: bigint(20)
    desc: 用户id
```

## 关联表

- [[cust_company_info]]：cust_project_code_record.company_id → cust_company_info.id（write-flow:CustProjectRelEnhanceService.java，confirmed）
