---
type: table
title: 客户变更配置
page_key: cust_change_cfg
domain: 基线
status: draft
anchors: [cust_change_cfg]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户变更配置

（基线页：27 字段，行数估计 139。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
desc: 客户变更配置
inactive: false
fields:
  - name: cust_type
    type: string
    phys: varchar(512)
    desc: 客户类型
    dict: cust_type
    topk: 1|2|3
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: identify_style
    type: string
    phys: varchar(512)
    desc: 认证方式
    dict: identify_style
    topk: INVITE|INVITE_AGW|SELF|SIMPLE
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
  - name: client_type
    type: string
    phys: varchar(20)
    desc: 端类型
    topk: ACCOUNT_PRODUCT|AGW
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
  - name: data_desc
    type: string
    phys: varchar(128)
    desc: 变更需要材料说明
    topk: 企业授权书|企业管理员身份证正反面|总公司法定代表人身份证正反面|总公司营业执照
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: beehive-scf.lianyirong.com.cn|beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: head_company
    type: string
    phys: varchar(10)
    desc: 是否总公司
    topk: N|Y
  - name: item_code
    type: string
    phys: varchar(128)
    desc: 变更项编码
    topk: UN0001|UN0002|UN0003|UN0004
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: open_process
    type: string
    phys: varchar(10)
    desc: 开启流程
    topk: N|Y
  - name: oper_item
    type: string
    phys: varchar(128)
    desc: 运营中台变更项
    topk: 企业授权书|增加企业角色|总公司变更为分公司|总公司法人手机号变更
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: plat_item
    type: string
    phys: varchar(128)
    desc: 平台变更项
    topk: 企业授权书|企业管理员业务邮箱变更|企业管理员变更|企业管理员手机号变更
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
```

## 关联表

- [[cust_change_record]]：cust_change_cfg.id → cust_change_record.alter_type_id（read-flow:CustSyncEventProcessor.java，confirmed）
- [[cust_person_info]]：cust_change_cfg.code → cust_person_info.ref_cust_company_info（java-eq:CustCompanyInfoApplication.java，suggested）
- [[cust_project_rel]]：cust_change_cfg.id → cust_project_rel.product_id（write-flow:PlatFormMigratoryApplication.java，confirmed）
