---
type: caliber
title: custBuildStatus 讯易链映射口径
page_key: cust-build-status-xyc-mapping
domain: 项目报表/统计/上报
status: draft
aliases:
  - 认证状态映射
  - convertCustBuildStatusToChinese
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
contract_version: "0.1"
belong: calibers
---

# custBuildStatus 讯易链映射口径

项目企业报表在讯易链来源下，需要把洞察平台的认证状态码翻译为中文展示：CUSTS003→认证成功，CUSTS005→待客户认证，CUSTS002/CUSTS001/CUSTS006→待审核，CUSTS004→审核拒绝。

## 需求背景

认证状态由外部系统以编码返回，报表侧需统一为中文文案供业务阅读。该映射只在讯易链分支使用（来源判定见 [[calibers/project-ledger-source]]）；多个编码归并为「待审核」说明外部状态机比展示态更细，报表侧做了收敛。

## 版本演进

CUSTS001/CUSTS002/CUSTS006 三码合并为「待审核」，属展示层收敛；未观察到映射表的更早版本或反向映射。

```ground:caliber
name: "custBuildStatus 讯易链映射口径"
predicate: "CUSTS003→认证成功；CUSTS005→待客户认证；CUSTS002/CUSTS001/CUSTS006→待审核；CUSTS004→审核拒绝"
scope: "项目企业报表认证状态中文展示"
evidence: "code_path:ProjectReportApplication.java:convertCustBuildStatusToChinese"
```