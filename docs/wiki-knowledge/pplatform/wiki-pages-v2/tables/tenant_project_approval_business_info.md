---
type: table
title: 租户项目审批业务系统推送信息表
page_key: tenant_project_approval_business_info
domain: 微企链立项与项目审批
status: draft
anchors: [tenant_project_approval_business_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 租户项目审批业务系统推送信息表

（基线页：34 字段，行数估计 416。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_business_info
database: lowcode_pplatform
desc: 租户项目审批业务系统推送信息表
fields:
  - name: asset_list_mode
    type: string
    phys: varchar(64)
    desc: 资产清单模式
    dict: asset_list_mode
    topk: "SIMPLE_LIST|STANDARD_LIST"
  - name: business_flow_mode
    type: string
    phys: varchar(64)
    desc: 业务流程模式
    dict: business_flow_mode
    topk: "CONFIRM_RIGHT_AFTER|CONFIRM_RIGHT_FIRST|先确权|后确权"
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
  - name: service_fee_min_flag
    type: string
    phys: varchar(64)
    desc: 服务费低消
    dict: service_fee_min_flag
    topk: "N|否|是"
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
    topk: "base|boscxsbl|sdhsg"
  - name: attachment_json
    type: string
    phys: text
    desc: 附件列表 JSON
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
    topk: "ISOLATE_TAG_boscxsbl|LN1|LN2|beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|spsi.beehive-scf.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: payer
    type: string
    phys: varchar(64)
    desc: 支付方
  - name: product_code
    type: string
    phys: varchar(64)
    desc: 产品编码code
    topk: "ACFLOW|ORDER|RVSFACTOR_PC"
  - name: project_config_version
    type: string
    phys: varchar(64)
    desc: 项目配置版本
    topk: "config|configPro"
  - name: quote_method
    type: string
    phys: varchar(64)
    desc: 报价方式
  - name: ref_tenant_project_approval_business_info_project_approval
    type: string
    phys: varchar(128)
    desc: 关联项目审批
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: review_fee
    type: string
    phys: varchar(64)
    desc: 审单费
    topk: "0|0.000000|1|1.000000|1.330000|10.000000|110.000000|198|200|280|90"
  - name: service_fee_collect_method_financing
    type: string
    phys: varchar(64)
    desc: 服务费收取方式
  - name: service_fee_collector_financing
    type: string
    phys: varchar(64)
    desc: 服务费收取方
    topk: "OPERATOR|PLATFORM|平台方|运营方"
  - name: service_fee_min_amount
    type: string
    phys: varchar(64)
    desc: 服务费低消金额
    topk: "0|100|200|200.000000|201.000000|2010.000000"
  - name: service_fee_quote_type_financing
    type: string
    phys: varchar(64)
    desc: 服务费报价类型
  - name: source_system
    type: string
    phys: varchar(64)
    desc: 来源系统
    topk: "ACFLOW|ORDER|RVSFACTOR_PC"
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
  - name: zhongdeng_register
    type: string
    phys: varchar(64)
    desc: 中登登记
```

## 关联表

- [[tenant_project_approval]]：tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval → tenant_project_approval.code（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project]]：tenant_project_approval_business_info.project_config_version → tenant_project.project_config_version（copy:ProjectBusinessConfigApplication.java，suggested）
