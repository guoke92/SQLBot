---
type: enum
title: source
page_key: tenant_setting_config__source
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---




# source

（权威枚举页：26 值，绑定方式 setter-evidence，主承载 tenant_setting_config.source；db 实测分布，基线外 1 值。）

```ground:enum
enum: tenant_setting_config__source
fields: [tenant_setting_config.source]
values:
  "75bd8802dd474f15b72b0fddb26b6fb7":
    label: "75bd8802dd474f15b72b0fddb26b6fb7"
    java_name: "PLATFORM_LOWCODE_PROJECT_CODE"
  "999999999":
    label: "999999999"
    java_name: "PLATFORM_COMPANY_ID"
  "pplatform":
    label: "pplatform"
    java_name: "PPLATFORM_SYSTEM"
  "APASS_TENABT_CODE":
    label: "APASS_TENABT_CODE"
    java_name: "RPC_TENANT_KEY"
  "scpr-pplatform-pc":
    label: "scpr-pplatform-pc"
    java_name: "BASE_SYS_CHANEL"
  "CustLicense":
    label: "CustLicense"
    java_name: "DATA_SOURCE_CUST_LICENSE"
  "CustPersonLicense":
    label: "CustPersonLicense"
    java_name: "DATA_SOURCE_CUST_PERSON_LICENSE"
  "BS_Auth":
    label: "BS_Auth"
    java_name: "DATA_SOURCE_BS_AUTH"
  "CFCA_Auth":
    label: "CFCA_Auth"
    java_name: "DATA_SOURCE_CFCA_AUTH"
  "CaUpgradeAuth":
    label: "CA 升级（重新开立 CA）授权书 —— 企业名称变更场景使用，模板 (DT_202605191387)。"
    java_name: "DATA_SOURCE_CA_UPGRADE_AUTH"
  "OfflineElectronicAuth":
    label: "线下授权书电子签约版 —— 与 (#DATA_SOURCE_CUST_LICENSE) 内容相同，独立 serviceKey，"
    java_name: "DATA_SOURCE_OFFLINE_ELECTRONIC_AUTH"
  "CaFeeAgreement":
    label: "CA 服务费收费协议"
    java_name: "DATA_SOURCE_CA_FEE_AGREEMENT"
  "UserProtocol":
    label: "String DATA_SOURCE_CUST_GROUP_LICENSE = \"Cust_Group_License\";"
    java_name: "DATA_SOURCE_USER_PROTOCOL"
  "PrivacyPolicy":
    label: "PrivacyPolicy"
    java_name: "DATA_SOURCE_PRIVACY_POLICY"
  "ProductProtocolAcflow":
    label: "ProductProtocolAcflow"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_ACFLOW"
  "ProductProtocolAms":
    label: "ProductProtocolAms"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_AMS"
  "ProductProtocolBeecredit":
    label: "ProductProtocolBeecredit"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_BEECREDIT"
  "ProductProtocolDealer":
    label: "ProductProtocolDealer"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_DEALER"
  "ProductProtocolOrder":
    label: "ProductProtocolOrder"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_ORDER"
  "ProductProtocolRvsfactor_PC":
    label: "ProductProtocolRvsfactor_PC"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_RVSFACTOR_PC"
  "ProductProtocolStorage":
    label: "ProductProtocolStorage"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_STORAGE"
  "ProductProtocolVoucher":
    label: "ProductProtocolVoucher"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_VOUCHER"
  "ProductProtocolDraft":
    label: "ProductProtocolDraft"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_DRAFT"
  "ProductProtocolDraftQa":
    label: "ProductProtocolDraftQa"
    java_name: "DATA_SOURCE_PRODUCT_PROTOCOL_DRAFT_QA"
  "ClearingBocomDebtor":
    label: "共同债务人合同文件源"
    java_name: "DATA_SOURCE_CLEARING_BOCOM_DEBTOR"
  "operUserLicense":
    label: "管理员子账号授权书"
    java_name: "DATA_SOURCE_OPER_LICENSE"
  "ACFLOW":
    label: "ACFLOW"
    note: "db 分布存在但代码枚举未声明（REVIEW）"
```
