---
type: caliber
title: 在途（未生效）迁移企业
page_key: on_the_way_company
domain: 租户迁移
status: draft
aliases: [在途企业口径, cust_status=ADD]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
belong: calibers
---

在途口径覆盖企业主体、人员、影像三条链路：企业建档状态 INIT、审核状态 null、人员状态强制 ADD、影像不接收授权书（CATGID_A0004 跳过）。与生效企业（EFFECT→BUILD_SUCCESS + CUST_CHECK_PASS）走完全不同分支，详见 [[在途]]、[[migratory_company_status_mapping]]、[[on_the_way_person_status_force]]。

```ground:caliber
name: 在途（未生效）迁移企业
predicate: "cust_company_info.cust_status = 'ADD'"
scope: "cust_build_status 置 INIT、check_status 置 null；人员 status 强制置 CustPersonStatusConstant.ADD，不采信上游推送状态"
evidence: "code:PlatFormMigratoryApplication.java#setCompany,#setPersonAdm,#setPersonOper"
```

## 需求背景

上游业务系统里"已建档未生效"的企业推过来时，不能直接进入产融生效口径（否则会误开通产品、误进入审核通过集合），需保持与上游一致的"在途"语义。

## 版本演进

早期由上游推送状态直落，现改为按 `cust_status` 派生本地状态并对人员状态强制覆写。