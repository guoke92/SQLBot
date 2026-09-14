---
type: rule
title: 迁移协议初始化（5 类，按客户+产品去重）
page_key: agreement_migratory_init
domain: 租户迁移
status: draft
aliases: [协议初始化, setAgreementMigratory]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setAgreementMigratory"
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
belong: rules
---

对每个产品编码，逐类 `count(custId + platformProductCode + agreementType)` 为 0 才插入一条待拉取记录，初始 `status='N'`、`pull_num=0`、`is_new=Y`。协议类型分支见 [[产品编码]]，后续拉取见 [[agreement_pull_status]]。

```ground:rule
name: 迁移协议初始化（5 类，按客户+产品去重）
content: "对每个产品编码，逐一 count(custId+platformProductCode+agreementType) 为 0 才插入：CA授权（AMS→BS_AUTH，其他→CFCA_AUTH）、产品协议（按产品分支）、企业授权书、用户协议、隐私政策；初始 status='N'、pull_num=0、is_new=Y"
impact: "为后续协议拉取任务生成待办清单"
field_targets:
  - argeement_migratory_record.cust_id
  - argeement_migratory_record.platform_product_code
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
evidence: "code:PlatFormMigratoryApplication.java#setAgreementMigratory + reqdoc:migratory-agreement-init"
```

## 需求背景

迁移时为迁移企业初始化协议待拉取记录，覆盖 CA 授权书、产品协议、企业授权书、用户协议、隐私政策五类；协议正文此时不搬，由后续任务回捞。

## 版本演进

CA 授权类型由单一类型演进为按产品分支（AMS→BS_AUTH，其他→CFCA_AUTH）；去重粒度固定为客户+产品+协议类型，保证重复迁移不产生重复待办。

相关：[[argeement_migratory_record]]、[[migratory_auth_supplement_flag]]。