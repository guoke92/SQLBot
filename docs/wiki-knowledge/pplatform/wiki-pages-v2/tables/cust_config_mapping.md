---
type: table
title: 企业信息配置表
page_key: cust_config_mapping
domain: 平台产品配置
status: draft
anchors: [cust_config_mapping]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












客户配置映射表 `cust_config_mapping` 承载「类型 + 内码 + 外码」形式的外部配置映射。在平台产品域中被复用的场景是把企业角色映射为平台产品编码：`getProductCompanyTypeConfig` 实际传参为 `(type='COMPANY_TYPE_MAPPING', innerCode=companyType, outerChannel=platformProductCode)`，即 `outer_channel` 存的是平台产品编码而非渠道。查询口径见 [[config_mapping_enabled]]，键名歧义见 [[config_mapping_filter_key]]。

## 需求背景

需求文档 BR-003 主张「平台产品扩展配置按 productCode+key+expectedValue 三元组查询 cust_config_mapping」。代码证据表明 `getProductExtConfig` / `getProductConfig` 实际读取 Nacos `app-list.yml` 的 extConfig / clientConfig（`nacosFacade.listProductApp()`），`cust_config_mapping` 仅服务于 `getConfig` / `listConfig` 的 `type+innerCode+outerChannel` 查询。该主张被证伪，本页以代码为准，扩展配置的真源见 [[product_ext_config_from_nacos]]。

## 版本演进

- 首次契约化即按「代码为准」记录 BR-003 的证伪结论；若后续需求文档修订，需同步本页与 [[product_ext_config_from_nacos]]。

```ground:table
table: cust_config_mapping
database: lowcode_pplatform
desc: 企业信息配置表
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
  - name: type
    type: string
    phys: varchar(64)
    desc: 类型
    dict: cust_config_mapping__type
    topk: "CHANGE_ITEM|COMPANY_MEDIA|COMPANY_TYPE_MAPPING"
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
    topk: "beehive-scf.qhhrly.cn"
  - name: groups
    type: string
    phys: varchar(32)
    desc: 分组
    topk: "BRANCH_COMPANY|HEAD_COMPANY"
  - name: inner_code
    type: string
    phys: varchar(32)
    desc: 内部编码
  - name: inner_name
    type: string
    phys: varchar(128)
    desc: 内部名称
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: outer_channel
    type: string
    phys: varchar(128)
    desc: 外部渠道
    topk: "ACFLOW|OPS|ORDER|SELF"
  - name: outer_code
    type: string
    phys: varchar(128)
    desc: 外部编码
    topk: "A0002|A0004|A0007|A0008|A0011|A0012|A0035|A0037|A0038|CE|CPT|OPE|PROJ|SPY|UN0001|UN0002|UN0005|UN0008|UN0011|UN0014"
  - name: outer_name
    type: string
    phys: varchar(128)
    desc: 外部名称
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

关联：[[platform_product]]、[[config_mapping_enabled]]、[[config_mapping_filter_key]]、[[product_ext_config_from_nacos]]