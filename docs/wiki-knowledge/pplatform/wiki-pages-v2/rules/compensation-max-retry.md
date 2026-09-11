---
type: rule
title: 补偿重试上限
page_key: rules/compensation-max-retry
domain: 平台事件监听与同步
status: draft
aliases:
  - maxRetryCount
  - MAX_RETRY_n
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
  - db:client_api_sync_error
contract_version: "0.1"
---

补偿重试有硬上限：retryCount 从 `returnData.retryCount` 读取，达到 maxRetryCount（默认 3）时标记 FAILED（remark 追加 `_FAILED_MAX_RETRY_3`），否则重试次数 +1 并回置 PENDING。

## 需求背景
无限重放会放大下游故障；因此补偿任务必须在「重试次数」与「终态」之间做取舍。该规则决定 [[processes/build-async-compensation-retry]] 的终态收敛，并与 [[calibers/client-sync-error-retry-num-3]] 中 DB 实测 `retry_num` 恒为 3 相互印证（默认上限一致）。

## 版本演进
- v0 契约：上限默认值 3，失败原因以 remark 后缀承载；终态后不再被 [[calibers/build-compensation-pending-records]] 扫描。

```ground:rule
name: 补偿重试上限
content: "retryCount 从 returnData.retryCount 读取，达到 maxRetryCount（默认3）时标记 FAILED（remark 追加 _FAILED_MAX_RETRY_3），否则重试次数+1并回置 PENDING"
impact: 决定补偿记录终态；DB中 retry_num 恒为3与默认上限一致
field_targets:
  - cust_build_record.retry_status
  - cust_build_record.return_data
evidence: "RegAsyncCompensationJobHandler.java:updateRetryCount + db:client_api_sync_error.retry_num=3"
related_pages:
  - processes/build-async-compensation-retry
  - calibers/client-sync-error-retry-num-3
```

---REVIEW: rule | 补偿重试上限---
本规则的证据跨两处：补偿侧 `updateRetryCount`（code）与 `client_api_sync_error.retry_num`（db）。后者属另一张表、另一条链路，语义分析以「默认上限一致」将二者关联；该等价性未经直接证据确认，标记待确认。
---END REVIEW---