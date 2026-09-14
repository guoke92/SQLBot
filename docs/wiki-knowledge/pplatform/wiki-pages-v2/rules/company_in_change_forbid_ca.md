---
type: rule
title: 企业变更中禁止开通 CA
page_key: company_in_change_forbid_ca
domain: CA证书认证
status: draft
aliases: [变更中禁止开通, cust_status=CHANGE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: rules
---

cust_status='CHANGE' 或 cust_build_status='CUST_CHANGE' 时抛异常「先走完变更流程再处理 CA 开通」。

**影响**：变更期间阻断 CA 预检与开通。变更完成后企业数据（法人、名称）可能已变，此前留存的核验材料需重新采集，因此不应在变更期间放行。

## 需求背景

规则读的是 [[cust_company_info]] 的变更相关字段；与 [[non_build_success_no_ca]] 的区别在于：本规则拦"正在变更"，后者拦"尚未成功建档"。

## 版本演进

- v0：首次固化两个触发字段与提示语。

```ground:rule
name: 企业变更中禁止开通 CA
content: "cust_status='CHANGE' 或 cust_build_status='CUST_CHANGE' 时抛异常「先走完变更流程再处理 CA 开通」"
impact: 变更期间阻断 CA 预检与开通
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
evidence: "code_path:CaCertificationPreCheckApplication.java#assertCompanyNotInChange"
```

关联页面：[[cust_company_info]]、[[non_build_success_no_ca]]、[[ca_open_operator_must_be_admin]]。