---
type: table
title: 客户接入密钥表
page_key: cust_access_secret
domain: 准入接入
status: draft
aliases: [接入密钥, 接入密钥信息, cust_access_secret]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "db: cust_access_secret 字段语义（语义分析 field_semantics）"
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java"
contract_version: "0.1"
---

`cust_access_secret` 是「准入接入与接入密钥」主题的核心主表，承载各接入渠道的密钥材料与租户归属信息。接入方以 `channel`（应用id/渠道标识）作为入口标识，系统据此取出 `db_tenant_code` 并设置租户上下文，因此该表既是鉴权入口，也是租户路由的起点。

从字段结构看，本表可划分为几组语义：

- **标识与渠道**：`id`（表主键）、`code`（编码）、`name`（名称）、`channel`（应用id/渠道标识，用于唯一标识接入渠道）。渠道语义的边界见 [[concepts/channel]]。
- **密钥材料**：`encry_type`（加密类型）、`pub_key`（公钥）、`pri_key`（私钥）、`password`（密码）、`key_num`（密钥对数量）、`rel_lls_secret_id`（关联平台密钥记录id）。这些字段共同决定了渠道侧的加解密与鉴权方式。
- **启停与备注**：`enable`（启用标识，Y=启用，N=禁用）、`remark`（备注）。启用语义见 [[concepts/enable]]，其判定口径见 [[calibers/access_secret_enable_valid]]。
- **审计字段**：`create_by` / `create_user` / `create_time` 与 `update_by` / `update_user` / `update_time`，分别记录创建与更新的人和时间。
- **流程字段**：`act_procinst_id`（流程实例ID）、`act_procinst_no`（流程申请编号）、`act_procinst_status`（当前审批状态）、`act_procinst_date`（审批结束时间），用于承载接入密钥相关审批流。
- **租户字段**：`app_tenant_code`（逻辑租户标识）、`db_tenant_code`（数据租户标识，用于多租户隔离；代码中通过渠道查询接入密钥后，用此字段设置租户上下文）。
- **机构与许可**：`organization_id`（机构编号）、`status_query_license_enabled`（建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否）。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；上述定位与字段说明全部来自库表语义与代码证据。

## 版本演进

- v0.1（本页）：依据 `cust_access_secret` 的库表字段语义与 `CustAccessApplication` 中的渠道校验代码建立首版契约，覆盖 26 个字段。字段级证据见下方锚点块。
- 与之相关的准入校验规则见 [[rules/channel_exists_and_enabled]]、[[rules/channel_tenant_exists]]、[[rules/company_build_duplicate_check]]、[[rules/tianma_company_build_duplicate_check]]。

```ground:fields
table: cust_access_secret
fields:
  - field: id
    meaning: 表主键
    evidence: db
  - field: code
    meaning: 编码
    evidence: db
  - field: name
    meaning: 名称
    evidence: db
  - field: channel
    meaning: 应用id/渠道标识，用于唯一标识接入渠道
    evidence: db
  - field: encry_type
    meaning: 加密类型
    evidence: db
  - field: pub_key
    meaning: 公钥
    evidence: db
  - field: pri_key
    meaning: 私钥
    evidence: db
  - field: password
    meaning: 密码
    evidence: db
  - field: key_num
    meaning: 密钥对数量
    evidence: db
  - field: rel_lls_secret_id
    meaning: 关联平台密钥记录id
    evidence: db
  - field: enable
    meaning: 启用标识，Y=启用，N=禁用
    evidence: db
  - field: remark
    meaning: 备注
    evidence: db
  - field: create_by
    meaning: 创建人id
    evidence: db
  - field: create_user
    meaning: 创建人名称
    evidence: db
  - field: create_time
    meaning: 创建时间
    evidence: db
  - field: update_by
    meaning: 更新人id
    evidence: db
  - field: update_user
    meaning: 更新人名称
    evidence: db
  - field: update_time
    meaning: 更新时间
    evidence: db
  - field: act_procinst_id
    meaning: 流程实例ID
    evidence: db
  - field: app_tenant_code
    meaning: 逻辑租户标识
    evidence: db
  - field: db_tenant_code
    meaning: 数据租户标识，用于多租户隔离；代码中通过渠道查询接入密钥后，用此字段设置租户上下文
    evidence: db
  - field: act_procinst_no
    meaning: 流程申请编号
    evidence: db
  - field: act_procinst_status
    meaning: 当前审批状态
    evidence: db
  - field: act_procinst_date
    meaning: 审批结束时间
    evidence: db
  - field: organization_id
    meaning: 机构编号
    evidence: db
  - field: status_query_license_enabled
    meaning: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
    evidence: db
```