---
type: caliber
title: 产品启用标记口径（enable）
page_key: product_enable_flag
domain: 租户产品
status: draft
aliases: [启用标记, enable]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_product_menu
  - db:tenant_product_menu_res
  - db:tenant_interworking_product
contract_version: "0.1"
belong: calibers
---

产品族四张表都带 enable 列，DB 实测均为 Y，出现「启用态恒定、关闭态靠删除实现」的口径特征。它与「开通状态」不是同一概念，见 [[concepts/product_open_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，查询侧默认只关心启用记录，因此 enable 更多是过滤条件而非业务状态。

## 版本演进
- 四表实测均为 Y，未观察到 N 样本，无法判断 N 是否仍在被写入。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 产品启用标记口径
fields:
  - table: tenant_product
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
  - table: tenant_product_menu
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
  - table: tenant_product_menu_res
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
  - table: tenant_interworking_product
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
```