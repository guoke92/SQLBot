---
type: table
title: 资金异常解析表（funding_exception_resolution）
page_key: tables/funding_exception_resolution
domain: funding
status: draft
aliases:
  - funding_exception_resolution
  - 异常解析表
  - 资金异常解析配置表
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_exception_resolution"
  - "db:funding_exception_resolution_un"
  - "code:ExceptionResolutionApplication"
  - "code:ExceptionResolutionImportListener"
  - "code:FundingPartyExceptionResolutionProviderImpl"
  - "code:PlatFormOperateAppliaction#getBussinessNo"
contract_version: "0.1"
---


# 资金异常解析表（funding_exception_resolution）

## 业务定位

该表是运营侧维护、外部系统消费的**异常解析配置字典**：把「某产品 + 某对接方」下出现的**报错关键字**映射到**报错原因**与**建议处理方案**，并允许挂附件。一条配置的业务主语由 `product_code + funding_party_code + error_keyword` 三元组确定，对外查询时并不直接按关键字等值取数，而是把该资方该产品下所有 `enable='Y'` 的配置拉回内存，用 `errorMessage.contains(error_keyword)` 做包含匹配，因此一次报错可以命中多条配置并全部返回。

`funding_party_code` 承载的是资方 RPC 返回的 fundingKey，而本表新建主键 `exception_no` 由 `PlatFormOperateAppliaction.getBussinessNo` 按 `fundingPartyCode` 生成，前缀为 `EXCEPTION_NO_<fundingPartyCode>`，即**异常编号与资方绑定**。

## 需求背景

本次语义分析中 `reqdoc_claims` 为空，没有任何需求文档锚点挂载到本表，因此上面的业务定位全部由代码与 DB 证据反推，不含文档声明。

## 版本演进

本表未出现 `action=uncovered` 的需求主张，故无 (document_claim，未证实) 条目。字段层面的可见演进事实：`file_path` 以 JSON 串 `{"files":[{"filePath":...}]}` 形式存储多附件，属后期扩展的结构；`product_code` 在 DB 实测仅出现 `ACFLOW` / `RVSFACTOR_PC` 两个值，说明该表最初可能只服务单一产品，随后扩展到多产品——但这属于推断，未被文档或迁移脚本证实。

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
desc: 资金方异常解析及建议主表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: error_keyword
    type: string
    desc: 报错关键字
  - name: error_reason
    type: string
    desc: 报错原因
  - name: exception_no
    type: string
    desc: 异常编号
  - name: file_path
    type: string
    desc: 附件
  - name: funding_party_code
    type: string
    desc: 对接方标识
  - name: funding_party_name
    type: string
    desc: 资金方名称
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: product_code
    type: string
    desc: 产品code
  - name: remark
    type: string
    desc: remark
  - name: suggestion
    type: string
    desc: 建议处理方案
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

## 关联

- 口径：[[calibers/exception_resolution_valid_enable_y]]、[[calibers/exception_resolution_unique_config]]
- 规则：[[rules/exception_import_all_or_nothing]]、[[rules/exception_unique_key_dedup]]、[[rules/exception_upsert_write]]、[[rules/exception_export_limit_50000]]、[[rules/exception_import_row_limit_5000]]、[[rules/exception_export_funding_party_name_acflow]]、[[rules/exception_provider_keyword_contains]]、[[rules/exception_provider_exception_fallback]]
- 概念：[[concepts/funding_party_code]]、[[concepts/funding_key]]、[[concepts/product_code]]