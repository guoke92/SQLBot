---
type: concept
title: 假贴牌
page_key: fake_oem
domain: 租户迁移
status: draft
aliases: []
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
maps_to: "无直接代码/DB对应，需求文档提及"
adjudication: boundary
also_confused_with: [自营贴牌]
contract_version: "0.1"
belong: concepts
---

(document_claim，未证实)

“假贴牌”出现在需求语料中，但语义分析明确标注为 boundary 判定：无直接代码/DB 对应。它与“自营贴牌”的边界是——假贴牌是自营下的二级贴牌，数据未隔离；代码中未找到“租户配置表单不可见”等实现。因此本页只承载术语边界，不承载任何字段锚点。

## 需求背景

(document_claim，未证实) 需求文档《产融平台数据迁移涉及的改造需求V1.2》主张：假贴牌迁移至产融平台后，在“租户配置”表单内不可见（仅存在于后台），作为自营贴牌的二级贴牌，内管端可正常创建该二级贴牌下的项目。该主张在语义分析中为 uncovered（无代码证据），仅作记录。

## 版本演进

- v0（草稿）：仅登记边界关系与别称缺失（aliases 为空）；一旦出现代码/库证据，应升级为带锚点的术语页或独立口径页。

关联页面：[[migratory_cust]]、[[migratory_tenant]]、[[tenant_migarory_log]]。