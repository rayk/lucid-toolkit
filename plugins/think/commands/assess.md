---
name: assess
description: Four-phase rigorous assessment protocol for solutions - gap analysis, framework selection, stress testing, and verdict
argument-hint: [solution or problem description to assess]
---

<objective>
Assess the solution or proposal described in $ARGUMENTS through a rigorous four-phase protocol.

Do NOT immediately provide a verdict. Process systematically through gap analysis, framework selection, stress testing, and final recommendation. This ensures solutions are evaluated with engineering rigor rather than surface-level approval.
</objective>

<process>

<phase name="interrogation" title="Gap Analysis">
Before evaluating *if* the solution works, determine if you have enough information to know.

1. **Identify Assumptions**: List all implicit assumptions the solution makes
   - Examples: "assuming infinite network bandwidth," "assuming user compliance," "assuming no concurrent access"

2. **Missing Constraints**: What critical variables are missing?
   - Budget limitations
   - Latency/performance requirements
   - Regulatory compliance (GDPR, SOC2, HIPAA)
   - Legacy system integration
   - Team expertise/capacity
   - Timeline constraints

3. **The "Black Box" Check**: Identify components described vaguely
   - Look for phrases like "then the data is processed," "the system handles it," "magic happens here"
   - Flag any component that lacks implementation detail

**Output**: A bulleted list of critical missing information required for full sign-off.
</phase>

<phase name="framework_selection" title="Framework Selection">
Based on the nature of the problem, select the most appropriate rigorous framework(s):

| Problem Domain | Applicable Frameworks |
|----------------|----------------------|
| Distributed Systems | CAP Theorem, Fallacies of Distributed Computing, PACELC |
| Security | STRIDE, Zero Trust, OWASP Top 10, Defense in Depth |
| Operations/Process | Theory of Constraints, Value Stream Mapping |
| Architecture | SOLID, 12-Factor App, Domain-Driven Design |
| Reliability | Chaos Engineering Principles, SRE Golden Signals |
| Data Systems | ACID vs BASE, Data Mesh Principles |
| Scalability | Little's Law, Amdahl's Law, Universal Scalability Law |

**Output**: State which framework(s) you are using and why they apply to this specific solution.
</phase>

<phase name="stress_test" title="Rigorous Evaluation">
Using the selected framework, critique the solution. Look for what breaks, not just what works.

1. **Edge Case Analysis**:
   - Extreme load (10x, 100x expected traffic)
   - Malicious input (SQL injection, XSS, buffer overflow attempts)
   - Hardware failure (disk, network, power)
   - Partial failures (degraded mode, split brain)
   - Clock skew and ordering problems

2. **Second-Order Effects**: If this solution succeeds, what new problems emerge?
   - Vendor lock-in risk
   - Technical/maintenance debt
   - Cognitive load on teams
   - Operational complexity increase
   - Cost scaling characteristics
   - Migration/exit strategy implications

3. **Single Points of Failure (SPOF)**: Identify bottlenecks that bring the whole system down
   - Network hops
   - Authentication services
   - Database connections
   - DNS resolution
   - Certificate authorities
   - Human dependencies (key person risk)
</phase>

<phase name="verdict" title="Verdict and Recommendation">
1. **Refined Solution**: Propose specific changes to address flaws found in Phase 3
   - Architectural modifications
   - Process improvements
   - Additional safeguards
   - Alternative approaches worth considering

2. **Confidence Score**: Rate the solution (0-100%) based ONLY on current information
   - 0-25%: Critical gaps prevent any meaningful assessment
   - 26-50%: Major concerns require resolution before proceeding
   - 51-75%: Viable with identified improvements
   - 76-100%: Sound approach with minor refinements needed

3. **Next Steps**: Define exactly what needs clarification to move to the next stage
   - Specific questions from Phase 1 that must be answered
   - Tests or proofs-of-concept recommended
   - Stakeholders who should review
</phase>

</process>

<success_criteria>
- All four phases completed in order
- Phase 1 produces specific, answerable questions (not vague concerns)
- Phase 2 selects frameworks with clear justification
- Phase 3 identifies concrete failure modes, not theoretical worries
- Phase 4 provides actionable recommendations with clear next steps
- Confidence score reflects actual information available, not optimism
- Output is structured and scannable for technical stakeholders
</success_criteria>
