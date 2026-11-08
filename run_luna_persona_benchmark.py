#!/usr/bin/env python3
"""
Live 24-Archetype / 320-Investor Benchmark & Bidirectional Stress Suite (gpt-6-luna)
====================================================================================
Executes:
  1. Spawns the complete 320-Investor Ecosystem across all 24 Unique Archetypes (IDs 2001..2320)
     plus Aether starting at $30,000 ($0.03M).
  2. Runs live parallel Multi-Batch gpt-6-luna calls for the 20 Smart Archetype Leads (IDs 2001..2020),
     local DNA-perturbed Conditional Playbooks for the 140 Smart Cohort Followers (IDs 2025..2164),
     and local Behavioral Finance algorithms for the 160 Savers/Retirees/FOMO/WSB Crowd (0 API cost).
  3. Verifies Smart Entrant Respawn Init via gpt-6-luna and Full-Fidelity Save/Load preservation.
  4. Saves full audit logs to logs/luna_ai_evaluation_report.json & logs/luna_ai_calls.jsonl.
"""

import os
import tempfile
import time
from eagle_capital_engine import EagleCapitalEngine
from luna_ai_orchestrator import LunaCohortOrchestrator, LOG_DIR


def main() -> None:
    jsonl_path = os.path.join(LOG_DIR, "luna_ai_calls.jsonl")
    if os.path.exists(jsonl_path):
        os.remove(jsonl_path)

    engine = EagleCapitalEngine()
    engine.set_street_hustler_30k_mode(player_id=1, cash_millions=0.03)
    cash_t0 = engine.total_closed_loop_cash()

    # Spawn all 320 Investors across all 24 Unique Archetypes (IDs 2001..2320)
    population = engine.spawn_full_320_investor_ecosystem(spawn_all_320=True)
    print(f"[INIT] Spawned {len(population)} investors across 24 Unique Archetypes (IDs 2001..2320) + Aether ($30,000 = $0.03M).")

    orchestrator = LunaCohortOrchestrator(engine=engine, model_name="gpt-6.1-luna")

    # Quarter 1: Full 20-Smart-Archetype-Lead Sweep (4 parallel calls) + 140 Playbook Followers + 160 Crowd
    # Quarter 2 & 3: Staggered Rotation (2 parallel calls/quarter) + Playbook Followers + 160 Crowd
    for q_step in range(1, 4):
        t0 = time.perf_counter()
        use_stagger = q_step >= 2
        res_ai = orchestrator.step_all_cohorts_quarterly(staggered_mode=use_stagger)
        engine.step_quarter()
        elapsed_s = time.perf_counter() - t0
        print(
            f"[Q{q_step} COMPLETE] Year {engine.year}-Q{engine.quarter} | "
            f"Luna API Batches: {res_ai['batches_called']} ({res_ai['smart_luna_decisions']} leads) | "
            f"Local Playbook Moves: {res_ai['local_playbook_moves']} | "
            f"Behavioral Crowd Moves: {res_ai['behavioral_moves']} | "
            f"Wipeout Respawns: {res_ai['respawns']} | "
            f"Wall Time: {elapsed_s:.2f}s"
        )

    # Test Smart Investor Wipeout -> gpt-6-luna Fresh Entrant Initialization
    smart_test_eid = 2019  # Alex V. ($30k Kelly Value Sniper)
    print(f"\n[SCENARIO TEST] Simulating wipeout of Smart Investor #{smart_test_eid} to test gpt-6-luna Fresh Entrant Init...")
    resp_info = engine.handle_investor_wipeout_and_respawn(smart_test_eid)
    init_ai_res = orchestrator.call_luna_for_smart_respawn_init(smart_test_eid)
    print(
        f"[SMART RESPAWN PASS] New Entrant: {resp_info['new_entrant_name']} | "
        f"Fresh Capital: ${resp_info['fresh_cash_millions']*1000:.1f}k | "
        f"Luna Init Decisions: {len(init_ai_res.get('decisions', []))}"
    )

    # Test Full-Fidelity Save/Load Roundtrip across the 320-investor world
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        save_path = tf.name
    try:
        engine.save_state(save_path)
        engine.load_state(save_path)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    report = orchestrator.generate_evaluation_report()
    inv = report["global_accounting_invariants"]
    cost_sum = report["api_cost_and_latency_summary"]
    qual_sum = report["ai_quality_and_diversity_metrics"]
    coupling = report["bidirectional_wsr_caplab_coupling"]

    print("\n=========================================================================")
    print(" LUNA AI (gpt-6-luna) 24-ARCHETYPE / 320-INVESTOR EVALUATION SUMMARY")
    print("=========================================================================")
    print(f" Model Used (Alias -> ID) : {report['requested_alias']} -> {report['model_evaluated']}")
    print(f" Total Population         : {report['total_investor_population']} Investors across {report['unique_archetypes_count']} Unique Archetypes")
    print(f" Total API Calls          : {cost_sum['total_api_calls']} calls")
    print(f" Total Tokens             : {cost_sum['total_tokens']:,} (Prompt: {cost_sum['total_prompt_tokens']:,}, Completion: {cost_sum['total_completion_tokens']:,})")
    print(f" Total Estimated USD Cost : ${cost_sum['total_estimated_cost_usd']:.6f} USD")
    print(f" Persona Fidelity Rate    : {qual_sum['persona_domain_fidelity_rate_pct']}% ({qual_sum['total_ai_decisions_evaluated']} AI decisions)")
    print(f" Engine Execution Rate    : {qual_sum['engine_action_execution_success_rate_pct']}%")
    print(f" Unique Strategic Theses  : {qual_sum['unique_strategic_theses_count']}")
    print(f" Wipeouts & Respawns      : {len(report['wipeout_and_respawn_graveyard'])} events")
    print(f" Bidirectional Coupling   : CapLab CapEx=${coupling['caplab_total_capex_millions']}M | GDP Impulse=+{coupling['real_gdp_impulse_pct']}% | CPI Push={coupling['urban_cpi_push_pct']}%")
    print(f" Closed-Loop Cash Delta   : {abs(engine.total_closed_loop_cash() - cash_t0):.6f} $M")
    print(f" 5-Regime Invariants OK   : {inv['ok']} (Max BS Err: {inv['max_balance_sheet_error']:.2e}, Share Err: {inv['max_share_conservation_error']:.2e})")
    print("=========================================================================")

    print("\n--- SAMPLE AI DECISIONS ACROSS THE 20 SMART ARCHETYPE LEADS ---")
    seen_arch = set()
    for d in orchestrator.decision_audit_log:
        pt = d["persona_type"]
        if pt not in seen_arch:
            seen_arch.add(pt)
            print(f" * [{pt}] {d['investor_name']} -> {d['executed_cmd']} {d['payload']}")
            print(f"   Thesis: \"{d['thesis']}\"")

    assert inv["ok"] is True, f"Global invariants failed: {inv}"
    assert abs(engine.total_closed_loop_cash() - cash_t0) < 1e-2, "Closed-loop cash conservation violated"


if __name__ == "__main__":
    main()
