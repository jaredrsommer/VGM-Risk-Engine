def risk_firewall(risk, crash_pressure):
    if crash_pressure > 0.75:
        return "BLOCK"
    if risk > 0.85:
        return "BLOCK"
    if risk > 0.60:
        return "REDUCE"
    return "ALLOW"