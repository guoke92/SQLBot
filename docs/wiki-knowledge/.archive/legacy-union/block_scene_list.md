---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 未缴费拦截场景
page_key: block_scene_list
domain: CA认证与服务费
aliases:
- 拦截业务
- 拦截节点
- 未缴费限制
anchors:
- block_scene_list
---
# 未缴费拦截场景

项目 block_scene_list 配置的四类拦截场景：GOTO_PRODUCT 门户进入业务系统、 FINANCE_APPLY 融资申请、RIGHTS_CONFIRM 确权申请、TRANSFER_SIGN 转让签收。 空列表=不拦截。

```ground:enum
enum: block_scene_list
fields:
- ca_fee_project_config.block_scene_list
values:
  GOTO_PRODUCT:
    label: 未缴费限制进入业务系统
  FINANCE_APPLY:
    label: 限制融资申请
  RIGHTS_CONFIRM:
    label: 限制确权申请
  TRANSFER_SIGN:
    label: 限制转让签收
```

## 关联
- [[ca_fee_project_config|ca_fee_project_config]]
