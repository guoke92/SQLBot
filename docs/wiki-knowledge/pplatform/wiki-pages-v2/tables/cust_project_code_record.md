---
type: table
title: 企业项目码录入记录表（cust_project_code_record）
page_key: table.cust_project_code_record
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_code_record
  - 企业项目码输入记录表
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:cust_project_code_record
contract_version: "0.1"
---

# 企业项目码录入记录表（cust_project_code_record）

cust_project_code_record 记录企业项目码的录入过程：录入来源、录入是否成功、以及提交时企业所持有的角色集合。它是「录入环节」的事实留存，与 [[tables/cust_project_rel]]（生效后的关联关系）构成前后两段：本表记录提交时的角色快照，关联表记录生效后的单值角色。

## 需求背景

企业注册与建站流程需要对企业输入的项目码做校验与留痕，区分来源渠道（用户自助注册 / PC 建站 / 产品中心 / 产品中心-企业认证成功），并记录该次提交是否正确。提交时企业可能同时具备多个角色，因此本表以 JSON 数组形式保存角色集合，作为审计与回溯依据；而项目台账侧的客户角色展示仍取关联表的单值字段，两者的差异见 [[concepts/company-type]]。

## 版本演进

本表字段的取值来源已演进为多渠道并存（userCompanyRegister、PC_BUILD、产品中心、产品中心-企业认证成功），说明录入入口从单一注册链路扩展为多入口；角色的多值化保存形态与关联表的单值形态长期并存，未见归一化动作。

```ground:fields
table: cust_project_code_record
fields:
  - name: status
    meaning: "企业项目码输入记录是否正确状态，Y/N"
    evidence: db
  - name: type
    meaning: "企业录入码来源类型：userCompanyRegister / PC_BUILD / 产品中心 / 产品中心-企业认证成功"
    evidence: db
  - name: company_type
    meaning: '该记录提交时的企业角色集合（JSON 数组形式，如 ["CORE","SUPPLIER"]）；与 cust_project_rel.company_type 单值形态不同'
    evidence: db
```