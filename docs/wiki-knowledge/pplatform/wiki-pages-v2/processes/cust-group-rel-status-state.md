---
type: process
title: 集团成员单位关系状态机
page_key: processes/cust-group-rel-status-state
domain: 企业集团关系
status: draft
aliases: [成员单位生效流程, cust_group_rel.status 状态机]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java
contract_version: "0.1"
---

本流程描述集团成员单位关系（[[tables/cust_group_rel]]）从新建到生效/拒绝的状态流转：新建即 INEFFECTIVE 并发待办，成员单位签署后 EFFECTIVE，拒绝则 REJECTED，运营端亦可直接生效。生效口径被 [[calibers/effective-group-member]] 与 [[rules/effective-member-no-op]] 引用。

## 需求背景

集团树中的成员关系必须经成员单位确认才具备业务效力，因此引入「未生效—已生效—已拒绝」三态与待办通知机制。运营端补录历史集团时允许按企业建档状态直接落生效或未生效。准入校验依赖企业建档成功（[[calibers/company-build-success]]），根节点不可作为被签对象（[[calibers/group-root-node]]）。协议签署与服务端直接生效两条路径并存，见 [[rules/effective-member-no-op]]。

## 版本演进

v0 契约按现状固化，三态基线来自代码枚举。现行实现中存在两条并存路径：一是成员单位协议签署（accept/reject），二是服务端 effectGroupRel 直接置生效；两者未在状态机层面统一收敛，后续版本可考虑合并为单一入口。新增子级的待办发送范围以企业建档成功为前提，见 [[rules/notice-only-build-success]]。

## 状态与迁移锚点

```ground:state_machine
name: 集团成员单位关系状态机
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效（待成员单位签署/处理待办）
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: "（新建）"
    event: 新增成员单位子级且企业认证成功，发送待办 sendCustGroupRelNotice(groupId)
    to: INEFFECTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java:sendCustGroupRelNotice
  - from: "（新建）"
    event: 运营端新增集团根节点 addExistRootGroupRel()：企业 cust_build_status=BUILD_SUCCESS 时直接置 EFFECTIVE，否则 INEFFECTIVE
    to: "EFFECTIVE | INEFFECTIVE"
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java:addExistRootGroupRel
  - from: INEFFECTIVE
    event: 签署协议 accept()（校验非 EFFECTIVE、rootFlag!=Y）
    to: EFFECTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java:accept
  - from: INEFFECTIVE
    event: 拒绝协议 reject()
    to: REJECTED
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java:reject
  - from: INEFFECTIVE
    event: effectGroupRel(custId,custType) 直接生效
    to: EFFECTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java:effectGroupRel
```