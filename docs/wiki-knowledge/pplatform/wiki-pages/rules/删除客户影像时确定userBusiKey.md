---
type: rule
title: 删除客户影像时确定userBusiKey
page_key: 删除客户影像时确定userBusiKey
belong: rules
domain: 文件媒体与附件
status: published
aliases: []
oid: 1
sources: [code, "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_build_record.person_id, cust_change_record.oper_cust_info]
scope:
  databases: [lowcode_pplatform]
---
本页记录规则「删除客户影像时确定userBusiKey」。该规则用于删除 A0004、A0011、A0012 影像时定位正确联系人，避免误删。

## 需求背景
代码路径 `CustMediaFacade.java:del` 显示：删除 A0004/A0011/A0012 影像时，需要从变更记录或建档记录中解析出 `userBusiKey` 和证件类型，并特殊处理 2025-08-01 之前的数据。该规则涉及 `cust_change_record.oper_cust_info`、`cust_build_record.person_id`、`cust_person_info.id` 等字段。

## 版本演进
v0.1 固化当前代码规则。2025-08-01 历史数据兼容逻辑仍可补充为显式迁移规则。

```ground:rule
name: 删除客户影像时确定userBusiKey
content: "删除A0004/A0011/A0012影像时，需要从变更记录或建档记录中解析出userBusiKey和证件类型，特殊处理2025-08-01之前的数据"
impact: "确保删除正确的影像，避免误删"
field_targets:
  - cust_change_record.oper_cust_info
  - cust_build_record.person_id
  - cust_person_info.id
evidence: "code_path:CustMediaFacade.java:del"
```

相关：[[cust_build_record]] [[cust_change_record]]
