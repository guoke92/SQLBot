---
type: table
title: CA服务费企业主数据
page_key: ca_fee_company
domain: 基线
status: draft
anchors: [ca_fee_company]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# CA服务费企业主数据

（基线页：33 字段，行数估计 1017。行语义/常用过滤待语义摄取增强。）

```ground:table
table: ca_fee_company
database: lowcode_pplatform
desc: CA服务费企业主数据
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: pay_status
    type: string
    phys: varchar(64)
    desc: 缴费状态：PAID 已缴费 / UNPAID 未缴费
    dict: pay_status
    topk: PAID|UNPAID
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
    topk: base
  - name: ca_status
    type: string
    phys: varchar(64)
    desc: CA签章状态
    topk: CANCELLED|NORMAL|UNKNOWN
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统一社会信用代码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_name
    type: string
    phys: varchar(512)
    desc: 企业名称
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1364399217692581890|1407266533295345665|1718930920919470081|1801438863791919106
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: linyanxiang|liuning|xiaolonghao|xuemengran
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_boscebl|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: ext_json
    type: string
    phys: text
    desc: 扩展字段 JSON预留
  - name: fee_locked
    type: string
    phys: varchar(2)
    desc: 是否已锁定年费标准
    topk: N|Y
  - name: locked_annual_fee
    type: number
    phys: int(10)
    desc: 首次缴费成功后锁定的年费标准（元）
    topk: 0|10|100|12
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
  - name: renew_remind_sent
    type: string
    phys: varchar(2)
    desc: 本期续费待办是否已生成：Y 已生成 / N 未生成
    topk: N|Y
  - name: service_end
    type: temporal
    phys: date
    desc: 当前 CA 服务费服务周期截止日（含）
  - name: service_start
    type: temporal
    phys: date
    desc: 当前 CA 服务费服务周期起始日（含）
  - name: source_company_type
    type: string
    phys: varchar(128)
    desc: 首次锁定来源企业角色，如 SUPPLIER/CORE
    topk: CORE|PROJECT_COMPANY|SUPPLIER
  - name: source_project_id
    type: number
    phys: bigint(20)
    desc: 首次锁定来源项目 ID
  - name: special_annual_fee
    type: number
    phys: int(10)
    desc: 特殊配置后应缴年费（元）
    topk: 0|10|100|12
  - name: special_config_flag
    type: string
    phys: varchar(2)
    desc: 是否存在生效中的特殊配置快照
    topk: N|Y
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 首次锁定来源租户
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1364399217692581890|1407266533295345665|1718930920919470081|1801438863791919106
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: linyanxiang|liuning|xiaolonghao|xuemengran
```

## 关联表

- [[ca_fee_order]]：ca_fee_company.source_project_id → ca_fee_order.project_id（write-flow:CaFeeOrderService.java，confirmed）
- [[cust_project_rel]]：ca_fee_company.code → cust_project_rel.ref_cust_project_rel_cust_company_info（java-eq:CaFeeRuleEngineService.java，suggested）
