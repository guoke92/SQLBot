---
type: rule
title: 成员单位删除前置在途校验
page_key: member_remove_check_business
domain: 集团关系
status: draft
aliases:
  - 删除成员单位在途校验
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 成员单位删除前置在途校验

`removeRootGroup` 先扁平化集团树，再调额度/产品在途校验，存在在途业务时抛 `HAS_BUSINESS_PROCESS`，阻断删除。

## 需求背景

成员单位可能已有额度或产品在途，直接删除会造成业务悬空，因此删除前必须整树校验。关系结构见 [[member_unit]]、[[cust_group_rel]]。

需求文档另主张“删除权限：不支持物理删除，只支持逻辑删除（冻结/注销）”。该主张**与代码不符**：`removeRootGroup` 最终调用 `groupRelService.removeBatchByIds(collect)`，集团成员单位关系是物理删除；文档所述“冻结/注销”在当前证据中未出现对应写值点。

## 版本演进

- 当前实现为物理删除 + 前置在途校验；若后续改为逻辑删除，本规则与删除链路需同步调整。

```ground:rule
name: 成员单位删除前置在途校验
content: removeRootGroup 先扁平化集团树，再调额度/产品在途校验，有在途业务抛 HAS_BUSINESS_PROCESS
impact: 阻断删除
field_targets:
  - cust_group_rel.id
  - cust_group_rel.root_cust_id
evidence: code_path:CustGroupRelApplication.java:validateBusinessOnWay
```