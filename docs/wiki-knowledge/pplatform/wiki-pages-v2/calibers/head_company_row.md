---
type: caliber
title: 总公司主体行口径
page_key: head_company_row
domain: CA证书认证
status: draft
aliases: [headCompanyData=Y, 总公司行]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationHeadCompanySupport.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

圈定分公司场景下以总公司主体信息落库的独立行：head_company_data='Y'。这类行的 cust_id 是总公司 id（cust_head_company_info.id），不是分公司在 cust_company_info 的 id，因此任何按 cust_id 关联企业主数据的查询都必须显式带上本口径，否则会把总公司行错配到分公司主体上。详见 [[head_company_data]]。

## 需求背景

总/分公司两行各自独立生成 batch_no，且在 [[incremental_idempotent_key|增量落库幂等键]] 中靠 head_company_data 区分。协议确认阶段只有 N 主行会被上送，见 [[confirm_submit_own_row_only]]；运营推送链路才会并行上送 N/Y 两行。

## 版本演进

- v0：首次固化谓词与分布值（Y=101 / 总行数 1367）。

```ground:caliber
name: 总公司主体行口径
predicate: "ca_certification_info.head_company_data = 'Y'"
scope: 分公司场景下以总公司四要素落库的独立行（db 分布 101/1367）
evidence: "code_path:CaCertificationHeadCompanySupport.java + db_dist:Y=101"
```

关联页面：[[ca_certification_info]]、[[head_company_data]]、[[incremental_idempotent_key]]、[[confirm_submit_own_row_only]]。