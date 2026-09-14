---
type: enum
title: agreement_type
page_key: agreement_type
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




# agreement_type

（权威枚举页：12 值，绑定方式 db-profile，主承载 argeement_migratory_record.agreement_type；db 实测分布。）

```ground:enum
enum: agreement_type
fields: [argeement_migratory_record.agreement_type]
values:
  "BS_Auth":
    label: "BS_Auth"
  "CFCA_Auth":
    label: "CFCA_Auth"
  "CustPersonLicense":
    label: "CustPersonLicense"
  "PrivacyPolicy":
    label: "PrivacyPolicy"
  "ProductProtocolAcflow":
    label: "ProductProtocolAcflow"
  "ProductProtocolAms":
    label: "ProductProtocolAms"
  "ProductProtocolBeecredit":
    label: "ProductProtocolBeecredit"
  "ProductProtocolOrder":
    label: "ProductProtocolOrder"
  "ProductProtocolRvsfactor_PC":
    label: "ProductProtocolRvsfactor_PC"
  "ProductProtocolStorage":
    label: "ProductProtocolStorage"
  "ProductProtocolVoucher":
    label: "ProductProtocolVoucher"
  "UserProtocol":
    label: "UserProtocol"
```
