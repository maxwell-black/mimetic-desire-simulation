"""
Verify paper_draft_16.md implements all 15 changes from the audit.
Run: python verify_draft16.py paper_draft_16.md
"""
import sys
import re

def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    msg = f"  [{status}] {label}"
    if detail and not condition:
        msg += f"\n         {detail}"
    print(msg)
    return condition

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_draft16.py <path_to_draft_16.md>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = text.split('\n')
    passed = 0
    failed = 0
    total = 0
    
    def do_check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if check(label, condition, detail):
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print("DRAFT 16 VERIFICATION")
    print("=" * 70)
    
    # CHANGE 0: Version header
    print("\n--- Change 0: Version header ---")
    do_check("Header says v16", "v16" in text[:500])
    do_check("No remaining v15 in header", "v15" not in text[:500])
    
    # CHANGE 1: Section 2.1 adaptive k + Appendix timesteps
    print("\n--- Change 1: Section 2.1 + Appendix C.8 ---")
    do_check("Adaptive k formula present", 
             "max(6" in text and "0.12" in text,
             "Should contain k = max(6, min(floor(0.12N), 20))")
    do_check("Extended timesteps in appendix",
             "50,000" in text or "50000" in text,
             "Appendix C.8 should mention extended run lengths")
    
    # CHANGE 2: Parameter sensitivity subsection + Table 2c
    print("\n--- Change 2: Parameter sensitivity ---")
    do_check("Phase Boundary Robustness heading present",
             "Phase Boundary Robustness" in text or "Parameter Sensitivity" in text)
    do_check("Table 2c present", "Table 2c" in text)
    do_check("5x4 grid: alpha=0.30 row present",
             "0.30" in text and "1.25" in text,
             "Should have alpha=0.30, delta=0.10 -> gamma*=1.25")
    do_check("exp3_param_sensitivity.py credited",
             "exp3_param_sensitivity" in text)
    do_check("Boundary nearly invariant to alpha claim",
             "invariant to" in text.lower() and "alpha" in text.lower())
    
    # CHANGE 3: Section 3.4 topology rewrite
    print("\n--- Change 3: Section 3.4 topology ---")
    do_check("N=50 scoping: 'At $N = 50$' qualifier",
             "At $N = 50$" in text and "robust across network topology" in text.lower(),
             "The topology robustness claim should be scoped to N=50")
    do_check("Topology Dependence at Scale heading",
             "Topology Dependence" in text)
    do_check("Table E1b present in Section 3.4",
             "Table E1b" in text)
    do_check("ER clustering 0.102 mentioned",
             "0.102" in text,
             "Erdos-Renyi clustering coefficient")
    do_check("BA peak modal 0.510 mentioned",
             "0.510" in text or "0.51" in text,
             "Barabasi-Albert peak modal")
    do_check("'flickering unanimity' or rapid target rotation concept",
             "flickering" in text.lower() or "target-switching" in text.lower() or "rotates" in text.lower() or "rotation" in text.lower(),
             "Should describe ER's rapid target switching phenomenon")
    do_check("exp5_topology_n200.py credited",
             "exp5_topology_n200" in text)
    do_check("Four failure modes enumerated",
             ("diffuse crisis" in text.lower() or "diffuse" in text.lower()) and 
             "bifurcation" in text.lower() and
             ("flickering" in text.lower() or "rotating" in text.lower()),
             "Should list: diffuse, bifurcation, flickering unanimity, cascade fragmentation")
    
    # CHANGE 4: Table 7 footnotes
    print("\n--- Change 4: Table 7 N=500 footnotes ---")
    # Check for dagger or footnote near Table 7
    do_check("Censoring footnote for N=500 in Table 7",
             ("dagger" in text.lower() or "†" in text or "censored at 1500" in text.lower()),
             "N=500 rows should be footnoted as censored")
    do_check("Two-thirds replacement for 'entire population'",
             "two-thirds" in text or "two thirds" in text or "~64%" in text or "approximately two-thirds" in text,
             "Line about grinding should say ~2/3, not 'entire population'")
    do_check("'entire population' NOT in grinding description",
             "grind through the entire population" not in text,
             "Old claim 'grind through entire population' should be removed")
    
    # CHANGE 5: Section 3.9 self-exhaustion revision
    print("\n--- Change 5: Section 3.9 self-exhaustion ---")
    do_check("Interpolation table with N=200-500",
             "63.8%" in text or "64.5%" in text or "63.3%" in text,
             "Should contain consumed fractions from interpolation data")
    do_check("N=50 90% exhaustion figure",
             "90%" in text and "18/20" in text,
             "N=50 should show 18/20 = 90% exhaustion")
    do_check("N=500 gamma=2.0 shows 30% exhaustion",
             "6/20" in text and ("30%" in text),
             "N=500 gamma=2.0: 6/20 genuine exhaustion")
    do_check("64% consumed fraction discussed as emergent constant",
             ("emergent constant" in text.lower() or "emergent" in text.lower()) and "64" in text,
             "~64% consumed fraction should be identified as emergent")
    do_check("self_exhaustion_interpolation.py credited",
             "self_exhaustion_interpolation" in text)
    
    # CHANGE 6: Section 3.10 2x2 at N=200
    print("\n--- Change 6: Section 3.10 ---")
    do_check("Section 3.10 heading present",
             "3.10" in text,
             "Should have a Section 3.10")
    do_check("Table 9 present",
             "Table 9" in text)
    do_check("AC peak modal 0.827 at N=200",
             "0.827" in text)
    do_check("RA peak modal 0.814 at N=200",
             "0.814" in text)
    do_check("'convergence preempted by' concept",
             "preempted" in text.lower() or "preempts" in text.lower(),
             "Should distinguish convergence preempted by exhaustion from mechanism failure")
    do_check("exp4_2x2_n200.py credited",
             "exp4_2x2_n200" in text)
    
    # CHANGE 7: Section 4.1 failure mode typology
    print("\n--- Change 7: Section 4.1 typology ---")
    do_check("Four-part failure typology in 4.1",
             "cascade fragmentation" in text.lower() or "fragmentation" in text.lower(),
             "Should enumerate: diffuse, bifurcation, flickering unanimity, fragmentation")
    
    # CHANGE 8: Section 4.3 sacred
    print("\n--- Change 8: Section 4.3 updates ---")
    do_check("64% in grinding regime discussion",
             "two-thirds" in text or "64%" in text,
             "Grinding regime should mention ~64% consumed")
    do_check("N=500 30% exhaustion in burst discussion",
             "30%" in text,
             "Should note only 30% exhaust at N=500 gamma=2.0")
    
    # CHANGE 9: Section 4.4 graduated transition
    print("\n--- Change 9: Section 4.4 ---")
    do_check("Specific exhaustion percentages in 4.4",
             "90%" in text and "80%" in text and "55%" in text and "30%" in text,
             "Should list: 90% at N=50, 80% at N=200, 55% at N=300, 30% at N=500")
    
    # CHANGE 10: Predictions 3 and 4
    print("\n--- Change 10: Predictions ---")
    do_check("Prediction 3: graduated self-exhaustion",
             "Prediction 3" in text and ("graduated" in text.lower() or "continuous decline" in text.lower()),
             "Prediction 3 should describe graduated, not binary, exhaustion")
    do_check("Prediction 4 present",
             "Prediction 4" in text,
             "Should have a new Prediction 4 about topology")
    do_check("Prediction 4 mentions topology/connectivity",
             "Prediction 4" in text and ("topology" in text.lower() or "connectivity" in text.lower()),
             "Prediction 4 should be about topology-dependent convergence")
    
    # CHANGE 11: Censoring paragraph rewrite
    print("\n--- Change 11: Censoring rewrite ---")
    do_check("5000-step data mentioned in censoring section",
             "5000 steps" in text or "5,000 steps" in text)
    do_check("k-note footnote present",
             "k-note" in text or "k_note" in text or ("ultra-long" in text.lower() and "adaptive" in text.lower()),
             "Should have footnote about k-bug in exp1 ultra-long runs")
    
    # CHANGE 12: Convergence metrics paragraph
    print("\n--- Change 12: Convergence metrics ---")
    do_check("Convergence metrics discussion in 4.6",
             "metric limitation" in text.lower() or "peak modal agreement" in text.lower(),
             "Should discuss peak modal as better metric than convergence rate")
    
    # CHANGE 13: Abstract
    print("\n--- Change 13: Abstract ---")
    # Find abstract (between ## Abstract and the next ---)
    abstract_match = re.search(r'## Abstract\s*\n(.*?)(?=\n---|\n## )', text, re.DOTALL)
    abstract = abstract_match.group(1) if abstract_match else ""
    
    do_check("Abstract: 50 to 500",
             "50 to 500" in abstract or "50-500" in abstract,
             "Abstract should say 50 to 500, not 50 to 200")
    do_check("Abstract: parameter robustness mentioned",
             "alpha" in abstract.lower() or "susceptibility" in abstract.lower() or "decay" in abstract.lower(),
             "Abstract should mention robustness across alpha/decay")
    do_check("Abstract: two-thirds / 64% consumed",
             "two-thirds" in abstract or "64" in abstract,
             "Abstract should mention characteristic consumed fraction")
    do_check("Abstract: graduated self-exhaustion",
             "90%" in abstract or "graduated" in abstract.lower() or "declines" in abstract.lower(),
             "Abstract should describe graduated, not binary, exhaustion")
    do_check("Abstract: topology dependence",
             "topology" in abstract.lower() or "connectivity" in abstract.lower(),
             "Abstract should mention topology-dependent convergence")
    do_check("Abstract does NOT say '50 to 200'",
             "50 to 200" not in abstract,
             "Old '50 to 200' range should be replaced")
    
    # CHANGE 14: Conclusion
    print("\n--- Change 14: Conclusion ---")
    # Find conclusion
    conc_match = re.search(r'## 5\. Conclusion\s*\n(.*?)(?=\n---|\n## |\Z)', text, re.DOTALL)
    conclusion = conc_match.group(1) if conc_match else ""
    
    do_check("Conclusion: 50 to 500",
             "50 to 500" in conclusion or "500" in conclusion,
             "Conclusion should say 50 to 500")
    do_check("Conclusion: 64% constant mentioned",
             "64%" in conclusion or "two-thirds" in conclusion,
             "Conclusion should mention 64% consumed fraction")
    do_check("Conclusion: topology/connectivity sentence",
             "connectivity" in conclusion.lower() or "topology" in conclusion.lower(),
             "Conclusion should mention topology-dependent convergence")
    
    # CHANGE 15: Appendix E Table E1b
    print("\n--- Change 15: Appendix E ---")
    # Count occurrences of Table E1b
    e1b_count = text.count("Table E1b")
    do_check("Table E1b appears in Appendix E",
             e1b_count >= 2,
             f"Table E1b appears {e1b_count} time(s); should be in both Section 3.4 and Appendix E")
    
    # STRUCTURAL CHECKS
    print("\n--- Structural checks ---")
    
    # Check section numbering
    sections = re.findall(r'^#{2,3} (\d+\.?\d*\.?\d*)', text, re.MULTILINE)
    do_check("Section 3.10 exists in numbering",
             "3.10" in sections,
             f"Found sections: {sections}")
    
    # Check no orphaned references to old table numbers
    do_check("No reference to 'Table 10' without Table 10 existing",
             "Table 10" not in text or text.count("Table 10") == text.count("*Table 10"),
             "Check for orphaned table references")
    
    # Check that "50 to 200" doesn't appear anywhere in the abstract or conclusion
    do_check("No stale '50 to 200' in abstract or conclusion",
             "50 to 200" not in abstract and "50 to 200" not in conclusion)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} passed, {failed}/{total} failed")
    if failed == 0:
        print("ALL CHECKS PASSED")
    else:
        print(f"WARNING: {failed} check(s) failed -- review above")
    print("=" * 70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
