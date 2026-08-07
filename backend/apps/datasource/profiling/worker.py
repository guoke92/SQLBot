"""Background worker that drains metadata_scan_run with leases."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from common.core.db import engine
from common.utils.utils import SQLBotLogUtil

from apps.datasource.profiling.models import ProfileStatus, ScanRunMode
from apps.datasource.profiling.service import (
    claim_next_run,
    mark_run_failed,
    mark_run_partial,
    mark_run_succeeded,
    new_worker_id,
)


def run_profiling_worker_once(*, max_jobs: int = 8) -> int:
    """Claim and execute up to ``max_jobs`` pending scan runs. Returns count."""
    maker = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    worker_id = new_worker_id()
    done = 0
    for _ in range(max(1, max_jobs)):
        with maker() as session:
            run = claim_next_run(session, worker_id=worker_id)
            if run is None:
                break
            run_id = int(run.id) if run.id is not None else None
            mode = (run.run_mode or ScanRunMode.FACTS_ONLY.value).strip()
            try:
                if mode not in {
                    ScanRunMode.FACTS_ONLY.value,
                    ScanRunMode.FULL.value,
                    ScanRunMode.SEMANTIC.value,
                    ScanRunMode.MANUAL.value,
                    ScanRunMode.VALIDATE.value,
                }:
                    raise ValueError(f"unsupported run_mode={mode}")

                from apps.datasource.profiling.bootstrap import run_facts_bootstrap

                needs_facts = True
                result: dict[str, Any]
                # full always recollects facts; semantic/manual/validate may reuse READY.
                if (
                    mode
                    in {
                        ScanRunMode.SEMANTIC.value,
                        ScanRunMode.MANUAL.value,
                        ScanRunMode.VALIDATE.value,
                    }
                    and run.table_id is not None
                ):
                    from apps.datasource.models.datasource import CoreTable

                    table = session.get(CoreTable, run.table_id)
                    if (
                        table is not None
                        and table.profile_status == ProfileStatus.READY.value
                        and int(table.active_profile_generation or 0) > 0
                        and (
                            not run.schema_fingerprint
                            or table.schema_fingerprint == run.schema_fingerprint
                        )
                    ):
                        needs_facts = False
                        result = {
                            "status": ProfileStatus.READY.value,
                            "fields": 0,
                            "skipped_facts": True,
                            "published": False,
                        }
                if needs_facts:
                    result = run_facts_bootstrap(session, run=run)
                SQLBotLogUtil.info(
                    f"profiling bootstrap run={run_id} mode={mode} result={result}"
                )
                if needs_facts and result.get("status") == ProfileStatus.FAILED.value:
                    detail = result.get("errors") or "field profile failed"
                    if isinstance(detail, list):
                        detail = "; ".join(str(x) for x in detail[:5])
                    mark_run_failed(session, run, str(detail))
                    done += 1
                    continue

                if mode == ScanRunMode.FACTS_ONLY.value:
                    _maybe_enqueue_semantic_followup(session, run=run, result=result)
                if mode in {
                    ScanRunMode.SEMANTIC.value,
                    ScanRunMode.FULL.value,
                    ScanRunMode.MANUAL.value,
                    ScanRunMode.VALIDATE.value,
                }:
                    if _agent_facts_ready(session, run=run, result=result):
                        _run_metadata_graph(session, run=run, mode=mode)
                    else:
                        SQLBotLogUtil.info(
                            f"profiling skip agent run={run_id}: facts not READY"
                        )

                _finalize_run(session, run=run, mode=mode, result=result, needs_facts=needs_facts)
                done += 1
            except Exception as exc:
                SQLBotLogUtil.error(f"profiling run={run_id} failed: {exc}")
                mark_run_failed(session, run, str(exc))
    return done


def _finalize_run(
    session: Session,
    *,
    run: Any,
    mode: str,
    result: dict[str, Any],
    needs_facts: bool,
) -> None:
    """Honest terminal status: SUCCEEDED only when the run's intent was met."""
    status = str(result.get("status") or "")
    if status == ProfileStatus.UNSUPPORTED.value:
        mark_run_succeeded(session, run)
        return

    attempted_profile = (
        needs_facts
        and not result.get("skipped_field_profile")
        and not result.get("skipped_facts")
        and mode
        in {
            ScanRunMode.FACTS_ONLY.value,
            ScanRunMode.FULL.value,
            ScanRunMode.MANUAL.value,
        }
    )
    if attempted_profile and not result.get("published"):
        detail = result.get("errors") or status or "profile generation not published"
        if isinstance(detail, list):
            detail = "; ".join(str(x) for x in detail[:5])
        mark_run_partial(session, run, detail=str(detail))
        return

    mark_run_succeeded(session, run)


def run_profiling_worker_drain(
    *,
    max_jobs_per_round: int = 8,
    max_rounds: int = 32,
) -> int:
    """Drain pending/expired-lease runs until idle or round budget exhausted."""
    total = 0
    for _ in range(max(1, max_rounds)):
        n = run_profiling_worker_once(max_jobs=max_jobs_per_round)
        total += n
        if n == 0:
            break
    return total


def _agent_facts_ready(
    session: Session, *, run: Any, result: dict[str, Any]
) -> bool:
    """Agent mining requires READY facts (or explicit structure-only skip)."""
    if result.get("skipped_field_profile"):
        return True
    if result.get("status") == ProfileStatus.READY.value:
        return True
    if result.get("skipped_facts") and run.table_id is not None:
        from apps.datasource.models.datasource import CoreTable

        table = session.get(CoreTable, run.table_id)
        return bool(
            table is not None
            and table.profile_status == ProfileStatus.READY.value
            and int(table.active_profile_generation or 0) > 0
        )
    return False


def _maybe_enqueue_semantic_followup(
    session: Session, *, run: Any, result: dict[str, Any]
) -> None:
    """Queue semantic mining when EffectivePolicy includes agent capabilities."""
    try:
        from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
        from apps.datasource.profiling.priority import is_high_value_table
        from apps.datasource.profiling.service import (
            enqueue_table_scan,
            resolve_table_mining_policy,
            schedule_worker_kick,
        )
        from sqlmodel import select

        if run.table_id is None:
            return
        # Only follow up when facts left a usable READY profile (or structure-only).
        if result.get("status") not in {
            ProfileStatus.READY.value,
            ProfileStatus.UNSUPPORTED.value,
        } and not result.get("skipped_field_profile"):
            return
        table = session.get(CoreTable, run.table_id)
        ds = session.get(CoreDatasource, run.ds_id)
        if table is None or ds is None:
            return
        policy = resolve_table_mining_policy(session, ds=ds, table=table)
        if not policy.has_agent_work():
            return
        field_count = len(
            session.exec(
                select(CoreField).where(
                    CoreField.table_id == table.id,
                    CoreField.checked == True,  # noqa: E712
                )
            ).all()
        )
        if not is_high_value_table(table, field_count=field_count):
            SQLBotLogUtil.info(
                f"semantic follow-up skipped low-value table={table.id}"
            )
            return
        enqueued = enqueue_table_scan(
            session,
            ds=ds,
            table=table,
            run_mode=ScanRunMode.SEMANTIC.value,
            trigger=run.trigger or "table_added",
            commit=True,
            skip_if_unchanged=False,
        )
        if enqueued is not None:
            schedule_worker_kick()
    except Exception as exc:
        SQLBotLogUtil.warning(f"semantic follow-up enqueue skipped: {exc}")


def _run_metadata_graph(session: Session, *, run: Any, mode: str) -> None:
    """Run the metadata mining graph; raise on failure so the scan is not marked OK."""
    from apps.conversation.outcome import outcome_is_success
    from apps.conversation.registry import get_graph
    from apps.datasource.profiling.graphs.nodes import build_metadata_state

    try:
        builder = get_graph("metadata")
    except KeyError as exc:
        raise RuntimeError("metadata graph not registered") from exc

    state = build_metadata_state(session, run=run, mode=mode)
    runnable = builder(state)
    if not hasattr(runnable, "invoke"):
        raise RuntimeError("metadata graph is not invokable")

    final = runnable.invoke(
        state if isinstance(state, dict) else {},
        config={"recursion_limit": 50},
    )
    if not isinstance(final, dict):
        return
    error = final.get("error")
    outcome = final.get("outcome")
    if error:
        raise RuntimeError(str(error))
    if outcome and not outcome_is_success(outcome):
        failures = outcome.get("failures") or []
        detail = failures[0].get("message") if failures else outcome.get("status")
        raise RuntimeError(f"metadata graph failed: {detail or 'unknown'}")
