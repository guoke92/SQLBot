---
type: table
title: 客户快捷入口配置
page_key: cust_customized_product
domain: 基线
status: draft
anchors: [cust_customized_product]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户快捷入口配置

（基线页：23 字段，行数估计 19。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_customized_product
database: lowcode_pplatform
desc: 客户快捷入口配置
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
    topk: base|dsjx
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1830871367974625282|1831884713207001090|1864237295142973442|1871148150314971138
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 13387654321|15121676382|15181221413|15312344321
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: LN1|beehive-scf.qhhrly.cn|dsjx
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: 图标
  - name: name
    type: string
    phys: varchar(128)
    desc: 产品名称
    topk: 1234568901234568901|12345689012345689011|4564564|AIO
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_cust_customized_product_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户关联自定义产品配置
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1830871367974625282|1831884713207001090|1864237295142973442|1871148150314971138
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 13387654321|15121676382|15181221413|15312344321
  - name: url
    type: string
    phys: varchar(512)
    desc: 跳转链接
    topk: 1111|1234568901234568901|12345689012345689011|23434
  - name: view_order
    type: number
    phys: int(10)
    desc: 显示顺序
```

## 关联表

- [[cust_company_info]]：cust_customized_product.ref_cust_customized_product_cust_company_info → cust_company_info.code（ref-convention:CustCustomizedProductDO.java，suggested）
