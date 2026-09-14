---
type: concept
title: 授权书（授权确认书）
page_key: auth_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 客户管理员授权确认书
  - 平台授权书
  - 授权协议
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
maps_to:
  - authorization_agreement.authed_status
field_targets:
  - authorization_agreement.authed_status
  - authorization_agreement.enable
  - authorization_agreement.cust_manager_id
adjudication: boundary
also_confused_with:
  - argeement_migratory_record.agreement_type
  - contract_info
belong: concepts
---

业务上说“授权书”，指的是企业管理员对产融平台的授权确认关系，落在 [[authorization_agreement]] 上，以 `authed_status`、`enable`、`cust_manager_id` 为关键字段，口径见 [[auth_agreement_authed_y]] 与 [[auth_agreement_authed_n]]。

它与业务协议文件是两件事：产品协议/隐私政策/用户协议/CA 协议等文件实体走 [[argeement_migratory_record]]（协议类型见 [[agreement_type]]），底层由协议组件合同表承载。做需求或排查时若把两者互换，会出现“授权书状态为 Y 但协议文件缺失”之类的误判。

## 需求背景
企业与平台之间的“授权”关系与“协议文件”关系在业务上被反复混用，本页用于固定词汇边界：凡是讨论“企业管理员是否已授权 / 是否需补签”“授权书签署触发条件”的，一律走本概念；凡是讨论“协议文件是否已拉取/存储路径/签署模式”的，一律走协议迁移记录。

## 版本演进
该词的别名随产品演进增加（客户管理员授权确认书、平台授权书、授权协议）；管理员变更作废、迁移企业免签等新规则都作用在本概念所指的记录上，见 [[manager_change_invalidate_agreement]]、[[migratory_supplement_exemption]]。