---
type: caliber
title: 最新成功上报数据
page_key: caliber/latest_success_report
domain: CA证书认证
status: draft
aliases: [最近一次成功上送, findLatestSuccessRow]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow"]
contract_version: "0.1"
---

口径含义：查询某企业最近一次成功上送签章中台的 CA 认证数据。过滤条件是 submit_status='SUCCESS' 且 enable='Y'，排序取 submit_time DESC、id DESC 的第一条。

这条口径是「结果态」而非「过程态」：PENDING 与 FAIL 的行都不进入结果集（状态语义见 [[processes/ca_certification_submit_status]]），被置为无效（enable='N'）的成功行同样被排除。调用方语义上应把该行视为该企业当前生效的 CA 认证事实。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。口径的谓词与排序字段均逐字来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。与口径相邻的另一条判定是 ca_register_status 的回写（[[rules/ca_invalidate_writeback]]）：当签章中台侧证书状态异常或登记名不一致时，企业侧标识被置为 N，前端据此引导重新开通，因此本口径的调用方需要与企业侧标识联合判断。

```ground:caliber
name: 最新成功上报数据
predicate: "ca_certification_info.submit_status = 'SUCCESS' 且 ca_certification_info.enable = 'Y'"
scope: 查询企业最近一次成功上送签章中台的数据，按 submit_time DESC, id DESC 取第一条
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow"
```

相关页面：[[tables/ca_certification_info]]、[[rules/ca_invalidate_writeback]]。