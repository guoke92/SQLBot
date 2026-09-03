---
type: rule
title: 身份证格式校验
page_key: id-card-format-validation
domain: 企业建档与准入
status: published
aliases: [身份证校验]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.legal_certification_no, cust_person_info.certification_no]
scope:
  databases: [lowcode_pplatform]
---

# 身份证格式校验

本规则要求身份证号必须为 18 位且符合身份证正则，适用于企业法人证件号与人员证件号。

## 需求背景

企业建档需采集法人身份证号，企业联系人/管理员需采集个人身份证号。格式校验在代码入口执行，验证失败抛出参数错误。

## 版本演进

证据来自代码路径 `CustAccessApplication.isValidIDCard`。

```ground:rule
name: 身份证格式校验
content: 身份证号必须为18位且符合身份证正则
impact: 验证失败抛出参数错误
field_targets:
  - cust_person_info.certification_no
  - cust_company_info.legal_certification_no
evidence: "code_path:CustAccessApplication.isValidIDCard"
```

相关表：[[cust_company_info]]、[[联系人_客户人员]]

相关：[[cust_person_info]]
