---
type: table
title: 租户项目审批业务系统推送信息表
page_key: tenant_project_approval_business_info
domain: 基线
status: draft
anchors: [tenant_project_approval_business_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目审批业务系统推送信息表

（基线页：34 字段，行数估计 416。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_business_info
database: lowcode_pplatform
desc: 租户项目审批业务系统推送信息表
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
    topk: base|boscxsbl|sdhsg
  - name: asset_list_mode
    type: string
    phys: varchar(64)
    desc: 资产清单模式
    topk: SIMPLE_LIST|STANDARD_LIST
  - name: attachment_json
    type: string
    phys: text
    desc: 附件列表 JSON
  - name: business_flow_mode
    type: string
    phys: varchar(64)
    desc: 业务流程模式
    topk: CONFIRM_RIGHT_AFTER|CONFIRM_RIGHT_FIRST|先确权|后确权
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1534087161817419777|1801438863791919106|1998571949021429761|2037353305376108546
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 刘倍材|刘宁|林彦湘|黄丽玉3
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_boscxsbl|LN1|LN2|beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
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
    topk: APPLICANT|CORE|SUPPLIER|融资申请人
  - name: product_code
    type: string
    phys: varchar(64)
    desc: 产品编码code
    topk: ACFLOW|ORDER|RVSFACTOR_PC
  - name: project_config_version
    type: string
    phys: varchar(64)
    desc: 项目配置版本
    topk: config|configPro
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
    topk: 0|0.000000|1|1.000000
  - name: service_fee_collect_method_financing
    type: string
    phys: varchar(64)
    desc: 服务费收取方式
    topk: BOCOM_PAY|FREE|OFFLINE|ONLINE
  - name: service_fee_collector_financing
    type: string
    phys: varchar(64)
    desc: 服务费收取方
    topk: OPERATOR|PLATFORM|平台方|运营方
  - name: service_fee_min_amount
    type: string
    phys: varchar(64)
    desc: 服务费低消金额
    topk: 0|100|200|200.000000
  - name: service_fee_min_flag
    type: string
    phys: varchar(64)
    desc: 服务费低消
    topk: N|否|是
  - name: service_fee_quote_type_financing
    type: string
    phys: varchar(64)
    desc: 服务费报价类型
    topk: FIXED|PLATFORM_SERVICE_RATE|TOTAL_RATE|固定利率
  - name: source_system
    type: string
    phys: varchar(64)
    desc: 来源系统
    topk: ACFLOW|ORDER|RVSFACTOR_PC
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1534087161817419777|1801438863791919106|1998571949021429761|2037353305376108546
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 刘倍材|刘宁|林彦湘|黄丽玉3
  - name: zhongdeng_register
    type: string
    phys: varchar(64)
    desc: 中登登记
    topk: BEFORE_REGISTER|中登登记啊大大|中登登记我是受让方|中登登记方服务
```

## 关联表

- [[tenant_project_approval]]：tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval → tenant_project_approval.code（java-eq:ProjectApprovalApplication.java，suggested）
