---
type: rule
title: 在途流程唯一性
page_key: applying_record_uniqueness
domain: 企业建档与认证
status: draft
aliases:
  - 禁止重复变更
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
  - reqdoc:企业状态为已冻结或已注销时不允许变更
contract_version: "0.1"
belong: rules
---

> (document_claim，未证实) 本页 ## 版本演进 含需求文档主张，尚未在代码中证实。

同一企业主数据下同时只允许存在一条在途流程：若还挂着未结束的申请数据（状态非 `BUILD_SUCCESS`/`BUILD_FAIL`），再次发起变更会被拒绝。判定依据见 [[calibers/judge_have_applying_record]]。

```ground:rule
name: 在途流程唯一性
content: 同一企业主数据存在未结束的 apply 数据(状态非 BUILD_SUCCESS/BUILD_FAIL)时禁止再次发起变更
impact: 重复变更被拒
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.data_type
  - cust_company_info.main_data_id
evidence: code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
```

## 需求背景

变更流程会改写主数据，若允许并行发起，两次流程的归档回写会互相覆盖（见 [[rules/apply_data_archive_to_main]]）。因此需要在发起前做在途判定，把并发收敛为串行。

## 版本演进

- v0 初稿：规则以 `judgeHaveApplyingRecord` 的实现固化。
- (document_claim，未证实) 需求文档主张"企业状态为已冻结或已注销时不允许变更"：代码侧对应校验位于 `custStatusOperator` 的 `config.getNeedCheckInWay()` 分支，该分支当前为 TODO 空实现，限制并未真正落地，需在开关实装后复核。

关联：[[processes/cust_build_status_state_machine]]、[[concepts/freeze]]、[[concepts/writeoff]]。

---REVIEW: rule | 在途流程唯一性---
- 在途校验开关 `needCheckInWay` 分支为空实现（TODO），无法确认冻结/注销企业的变更限制是否已生效；当前仅能确认"未结束流程即拒绝"这一路径。
---END REVIEW---