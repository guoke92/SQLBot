---
type: enum
title: source
page_key: tenant_project__source
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
belong: enums
---

# source

（权威枚举页：6 值，绑定方式 setter-evidence，主承载 tenant_project.source；db 实测分布，基线外 5 值。）

```ground:enum
enum: tenant_project__source
fields: [tenant_project.source, tenant_setting_config.source, tenant_setting_config_share.source]
values:
  CaUpgradeAuth:
    label: CA 升级（重新开立 CA）授权书 —— 企业名称变更场景使用，模板 (DT_202605191387)。
  OfflineElectronicAuth:
    label: 线下授权书电子签约版 —— 与 (#DATA_SOURCE_CUST_LICENSE) 内容相同，独立 serviceKey，
  CaFeeAgreement:
    label: CA 服务费收费协议
  UserProtocol:
    label: String DATA_SOURCE_CUST_GROUP_LICENSE = "Cust_Group_License";
  ClearingBocomDebtor:
    label: 共同债务人合同文件源
  operUserLicense:
    label: 管理员子账号授权书
  ACFLOW:
    label: "ACFLOW"
    note: db 分布存在但代码枚举未声明（REVIEW）
  ORDER:
    label: "ORDER"
    note: db 分布存在但代码枚举未声明（REVIEW）
  RVSFACTOR_PC:
    label: "RVSFACTOR_PC"
    note: db 分布存在但代码枚举未声明（REVIEW）
  STORAGE:
    label: "STORAGE"
    note: db 分布存在但代码枚举未声明（REVIEW）
  pplatform:
    label: "pplatform"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
