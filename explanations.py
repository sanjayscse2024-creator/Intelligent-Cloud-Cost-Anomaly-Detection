def explain(row):
    facts = [f"Actual cost was {row['cost']:.2f} versus baseline {row['baseline_cost']:.2f}.", f"The absolute difference was {row['absolute_difference']:.2f} ({row['percentage_difference']:.1f}% where a non-zero baseline exists).", f"Detection method: {row['method']}; history points: {int(row['history_points']) if row['history_points']==row['history_points'] else 0}."]
    hypotheses = ["Review recent deployments, traffic/usage changes, pricing or commitment changes, and billing dimensions."]
    if row.get('direction') == 'drop': hypotheses.append("A drop may reflect reduced usage, credits, service outage, or delayed billing; verify before treating it as savings.")
    recs = ["Compare the same service/project/region against the billing console and usage metrics.", "Check tags, rate-card changes, credits/refunds, and period completeness.", "Do not automatically change infrastructure; record reviewer evidence and next steps."]
    return {"facts": facts, "hypotheses": hypotheses, "recommendations": recs}
