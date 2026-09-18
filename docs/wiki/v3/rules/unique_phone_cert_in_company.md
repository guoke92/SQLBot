---
type: rule
title: 同一企业下手机号和证件号不可重复
page_key: unique_phone_cert_in_company
belong: rules
domain: cust
status: draft
field_targets: [cust_person_info.phone, cust_person_info.certification_no, cust_person_info.ref_cust_company_info]
sources: ['code_path:CustPersonApplication.java:348']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info]
---

# 同一企业下手机号和证件号不可重复

checkBeforeSave 按企业 code 列出全部联系人（不过滤 enable）校验手机号、证件号。
已冻结（enable=N）的旧行仍占用号码，不能靠冻旧绕过本规则。


```ground:rule
rule: 同一企业下手机号和证件号不可重复
field_targets: [cust_person_info.phone, cust_person_info.certification_no, cust_person_info.ref_cust_company_info]
impact: write_constraint
content: 'checkBeforeSave 按企业 code 列出全部联系人（不过滤 enable）校验手机号、证件号。

  已冻结（enable=N）的旧行仍占用号码，不能靠冻旧绕过本规则。

  '
evidence: code_path:CustPersonApplication.java:348
```

## 页面链接

- [[tables/cust_person_info]]
