---
type: rule
title: group根企业禁操作
page_key: root_group_no_operation
domain: 集团关系
status: draft
aliases:
  - 根节点禁止签署
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# group根企业禁操作

`root_flag='Y'` 或状态已 `EFFECTIVE` 的集团关系，不允许再次执行 accept/reject。

## 需求背景

根企业自身不存在“被上级邀请签署”的场景，已生效关系重复签署也会造成状态回退，因此需要前置拦截，见 [[group_root_node]]、[[effective_group_rel]]、[[cust_group_rel_status]]。

## 版本演进

- 拦截在 `checkCustGroup` 中完成，属应用层校验；直接调用底层状态更新接口不受此约束。

```ground:rule
name: group根企业禁操作
content: root_flag='Y' 或状态已 EFFECTIVE 的集团关系不允许再次 accept/reject
impact: 阻断
field_targets:
  - cust_group_rel.root_flag
  - cust_group_rel.status
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```