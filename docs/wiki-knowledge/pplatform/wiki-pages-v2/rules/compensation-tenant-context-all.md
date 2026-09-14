---
type: rule
title: 补偿任务租户上下文全量查询
page_key: compensation-tenant-context-all
domain: 平台事件监听与同步
status: draft
aliases:
  - dbTenantCode='all'
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords/processCompensationRecord
contract_version: "0.1"
belong: rules
---

租户上下文规则：补偿任务查询时设置 `dbTenantCode='all'` 全量扫描，处理单条时再按 `record.dbTenantCode` 还原租户上下文。

## 需求背景
补偿任务是后台任务，不承载具体请求的租户上下文；若按当前租户过滤，会漏扫其他租户沉积的失败记录。因此查询阶段放开租户过滤，处理阶段再切回记录自身的租户，保证重放时数据源指向正确。扫描口径见 [[calibers/build-compensation-pending-records]]。

## 版本演进
- v0 契约：规则取自 `getCompensationRecords/processCompensationRecord`；「all」的取值约定属实现细节，未在语义分析中展开。

```ground:rule
name: 补偿任务租户上下文全量查询
content: "补偿任务查询时设置 dbTenantCode='all' 全量扫描，处理单条时再按 record.dbTenantCode 还原租户上下文"
impact: 跨租户补偿记录可见性
field_targets:
  - cust_build_record.db_tenant_code
evidence: "RegAsyncCompensationJobHandler.java:getCompensationRecords/processCompensationRecord"
related_pages:
  - tables/cust_build_record
  - calibers/build-compensation-pending-records
```