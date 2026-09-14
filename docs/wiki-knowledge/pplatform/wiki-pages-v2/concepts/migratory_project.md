---
type: concept
title: 迁移项目
page_key: migratory_project
domain: 租户迁移
status: draft
aliases: [migratoryProject]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
maps_to: "tenant_migarory_log.type = 'migratoryProject' 或 name = '迁移项目'"
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
belong: concepts
---

“迁移项目”是业务侧对项目级迁移动作的称呼，库中以类型码 `migratoryProject` 出现，二者同义（adjudication: synonym），在 [[tenant_migarory_log]] 上分列 type 与 name，取数口径见 [[migration_project_log]]。

## 需求背景

术语映射来自 DB 值分布；注意与项目**同步**（`PROJECT_SYNC`）区分：同步是数据方向上的动作，不改变本术语的迁移语义。

## 版本演进

- v0（草稿）：synonym 判定成立。
- (document_claim，未证实) 需求文档《产融平台数据迁移涉及的改造需求V1.2》提及“产融新建租户和定制项目映射表；新增项目时选择产品后需选择定制项目标识；租户迁移接口需调整，自营租户存储映射关系；项目迁移存储定制项目标志；项目同步接口添加项目标志；运营方多项目测试数据的打标处理”。该主张在语义分析中标记为 uncovered（无代码证据），本页仅作记录，不产生锚点，也不改变现有 `migratoryProject` 映射。

关联页面：[[tenant_migarory_log]]、[[migration_project_log]]、[[migratory_tenant]]。