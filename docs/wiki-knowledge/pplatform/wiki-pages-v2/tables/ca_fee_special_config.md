---
type: table
title: CA服务费特殊企业配置
page_key: ca_fee_special_config
domain: 基线
status: draft
anchors: [ca_fee_special_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# CA服务费特殊企业配置

（基线页：25 字段，行数估计 55。行语义/常用过滤待语义摄取增强。）

```ground:table
table: ca_fee_special_config
database: lowcode_pplatform
desc: CA服务费特殊企业配置
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
  - name: annual_fee
    type: number
    phys: int(10)
    desc: 年费标准
    group: annual_fee_group
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
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
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: operate_logs
    type: string
    phys: text
    desc: 操作日志
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 项目id
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
    topk: 1|11|111|3
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
  - name: valid_end
    type: temporal
    phys: date
    desc: 有效期止
  - name: valid_start
    type: temporal
    phys: date
    desc: 有效期起
```
