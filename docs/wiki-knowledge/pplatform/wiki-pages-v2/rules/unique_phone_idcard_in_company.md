---
type: rule
title: 企业内手机号/身份证号唯一
page_key: unique_phone_idcard_in_company
domain: 经办人/联系人/管理员管理
status: draft
aliases: [手机号唯一, 身份证唯一, checkBeforeSave]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#checkBeforeSave"]
contract_version: "0.1"
belong: rules
---

新增/编辑联系人前的强制校验：同一企业（ref_cust_company_info）下手机号或身份证号不允许重复，命中即抛业务异常并中断保存（[[cust_person_info]]）。

## 需求背景
- 手机号在库内是密文存储，校验需先做加密比较，因此该校验与普通字段唯一性校验实现方式不同（[[cust_person_info]]、[[valid_person]]）。

## 版本演进
- 当前版本按企业维度汇总存量后比对，跨企业不拦截。

```ground:rule
name: 企业内手机号/身份证号唯一
content: "保存联系人前按 ref_cust_company_info 汇总存量，手机号或身份证号重复则抛“当前组织下已存在手机号【x】成员！/身份证号【x】成员！”"
impact: 新增/编辑联系人被拦截
field_targets:
  - cust_person_info.phone
  - cust_person_info.certification_no
  - cust_person_info.ref_cust_company_info
evidence: "code_path:CustPersonApplication.java#checkBeforeSave"
```

相关页面：[[cust_person_info]]、[[unique_admin_per_company_role]]、[[valid_person]]。