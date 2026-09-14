---
type: rule
title: 线下电子授权书签署触发条件（多重与门）
page_key: offline_eauth_sign_trigger
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子授权书触发条件
  - off_auth 签署与门
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
  - db:cust_change_record
  - db:tenant_setting_config
contract_version: "0.1"
belong: rules
---

这是本主题最核心的规则：电子授权书签署不是单条件触发，而是六个与门同时成立。任一条件不满足时**仅记日志跳过**，不阻断主流程——这一点决定了线上问题往往表现为“没有签”，而不是“报错”。

涉及口径：[[tenant_electronic_auth_flag]]、[[need_register_ca]]、[[cfca_registered]]、[[auth_agreement_supplement_flag]]；相关表 [[cust_company_info]]、[[cust_change_record]]、[[cust_change_cfg]]、[[tenant_setting_config]]。

```ground:rule
name: 线下电子授权书签署触发条件（多重与门）
content: "仅当 ①审核通过(checkStatus=CUST_CHECK_PASS) ②授权模式为 off_auth ③租户 generate_electronic_auth_flag=Y ④企业类型∈{供应商,核心企业,金融机构,项目公司} ⑤建档流程且建档方式∈{INVITE客户录入,SELF自主注册} 或 变更流程且 alterMode=SELF_ALTER 且变更项∈{UN0016,UN0012,UN0013,UN0008,UN0015} ⑥need_register_ca=Y 且 ca_register_status=Y 时，才在事务提交后触发签署；任一不满足仅记日志跳过，不阻断主流程"
impact: "决定线下授权书是否自动发起电子签署"
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.identify_style
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_change_record.alter_mode
  - cust_change_record.alter_type_id
  - tenant_setting_config.generate_electronic_auth_flag
evidence: "code:CustAuthSignOrchestrationApplication.java:evaluateIneligibilityReason + isCaRegistered"
```