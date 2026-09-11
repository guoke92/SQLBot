---
type: caliber
title: 产融项目运营人员离职提示口径
page_key: caliber.deleted-operator-hint-for-chanyong
domain: 项目报表/统计/上报
status: draft
aliases:
  - 离职提示口径
  - checkDeletedOperatorsForCompanies
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
contract_version: "0.1"
---

# 产融项目运营人员离职提示口径

当产融来源的项目被标记为置顶/需关注时，系统挑出该项目下角色为核心（CORE）与金融（FINANCE）且有效的关联记录，检查其运营对接人是否已离职，并把提示文本回写到台账 text 字段。

## 需求背景

置顶项目需要重点跟进，若对接人已离职则必须提示，避免出现无人响应的项目。角色限定为 CORE/FINANCE，说明仅这两类角色的对接人被视为关键联系人；离职判定使用统一的人员口径（见 [[calibers/deleted-operator]]）。相关字段定义见 [[tables/cust_project_rel]]。

## 版本演进

提示能力以 `top_flag = '1'` 为触发条件，属「需关注」场景的扩展能力；未观察到提示范围从 CORE/FINANCE 进一步扩大的证据。

```ground:caliber
name: "产融项目运营人员离职提示口径"
predicate: "cust_project_rel.project_id = :projectId AND top_flag = '1' AND company_type IN ('CORE','FINANCE') AND enable = 'Y'"
scope: "项目台账 text 字段生成（产融来源）"
evidence: "code_path:ProjectReportController.java:checkDeletedOperatorsForCompanies"
```