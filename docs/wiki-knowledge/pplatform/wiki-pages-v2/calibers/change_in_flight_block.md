---
type: caliber
title: "变更在途阻断"
page_key: "calibers/change_in_flight_block"
domain: "customer-onboarding"
status: draft
aliases:
  - "在途变更阻断"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustPersonApplication.java:adminChangeSaveOrUpdate"
  - "code_path:CustCompanyIfoEnchanceService.java:isOpenCa"
contract_version: "0.1"
---

企业存在在途变更时，主表 `cust_status` 处于变更中状态，此时新的变更提交与部分能力（如 CA 开通）会被阻断并给出显式提示。这是「同一企业同一时刻只允许一条变更流程」的口径表达。状态载体见 [[tables/cust_company_info]]，变更记录见 [[tables/cust_change_record]]。

## 需求背景

需求文档要求变更须经审核并生效，为保持审核对象唯一，需要阻断并发的第二笔变更。

## 版本演进

- 阻断点从变更提交入口扩展到能力开通入口，两处均以同一字段值判定，见 [[processes/change_record_check_machine]]。

```ground:caliber
name: "变更在途阻断"
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: "adminChangeSaveOrUpdate 抛『有在途变更流程，请检查!』；isOpenCa 阻断『企业信息变更流程处理中』"
evidence: "code_path:CustPersonApplication.java:adminChangeSaveOrUpdate;CustCompanyIfoEnchanceService.java:isOpenCa"
```

相关：[[tables/cust_company_info]]、[[processes/change_record_check_machine]]、[[concepts/build_status]]。