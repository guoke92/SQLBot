---
type: caliber
title: 有效企业
page_key: valid_company
domain: 平台内部服务对接
status: draft
aliases:
  - 有效企业口径
  - 企业启用过滤
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「有效企业」是查询 [[cust_company_info]] 时的默认过滤条件：启用状态为 Y。内部服务在按编码或名称取企业主数据时，若不附加该条件，可能取到已停用的企业记录，因此新建或临时企业的流程也沿用同一口径。该口径只表达启用与否，与企业状态机（见 [[cust_status_flow]]）中的冻结、注销是两个维度，组合使用时需要分别判断。

## 需求背景
企业可能被停用但历史数据仍需保留，因此不能通过删除记录来屏蔽；把「有效」固化为一个可复用的过滤条件，能让客户侧与运营侧服务得到一致的企业可见范围。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析。

```ground:caliber
name: 有效企业
predicate: "cust_company_info.enable = 'Y'"
scope: 查询企业主数据时默认过滤条件
evidence: "code_path:PlatFormRvsApplication.java:getAndCreateTempCompany"
```