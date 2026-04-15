AI-Augmented Sustainability & Climate Risk Workflow
How I've Configured Claude Code for Sustainability and Climate Consulting Work
Taylor Black | April 2026

What This Is
This document explains the reasoning behind the Claude Code configuration in this project. The CLAUDE.md file in the root of this repository is not boilerplate. It is a deliberate set of instructions that shapes how an AI agent behaves when working through a sustainability and climate transition planning engagement. This explainer walks through what I built, why I sequenced it the way I did, and what it makes possible.

What This Automates
Sustainability and climate transition planning engagements are methodologically dense and repetitive across clients. The same tasks recur on every project: extracting and cleaning energy consumption data from utility bills and receipts, applying emission factors to calculate Scope 1, 2, and 3 inventories, scoring physical and transition risk exposures against scenario benchmarks, structuring materiality assessments around a consistent IRO register, and assembling disclosure narratives that satisfy multiple overlapping frameworks simultaneously.
Each of these tasks is time-consuming not because it requires deep judgment at every step, but because it requires consistent methodology applied carefully across large volumes of data and text. That is exactly what a well-configured AI agent is good at.
The CLAUDE.md configuration automates the methodological scaffolding: the framework choices, the scoring rubrics, the output formats, and the quality checks. This frees the consultant's judgment to focus on the parts that actually require it: interpreting results, advising clients, and making calls that require experience rather than pattern-matching.
Specifically, this configuration automates:

GHG inventory calculations with built-in source citation requirements and confidence scoring
Physical and transition risk scoring using defined scenario frameworks and asset-level methodology
IRO identification and scoring for double materiality assessments
SBTi target gap analysis against current emissions trajectories
First-draft disclosure language structured to IFRS S2 and CSRD ESRS E1 simultaneously


How the Sequence Mirrors a Real Engagement
The six-step project structure is not arbitrary. It follows the actual sequence a consultant works through when delivering a climate transition planning mandate for a corporate client.
Step 1 - Configuration comes first because AI-augmented work requires upfront investment in methodology definition. A consultant who opens an AI tool without configuring it for the domain will get generic outputs. The CLAUDE.md is the equivalent of an engagement kickoff: establish the frameworks, define the outputs, set the quality bar before any work begins.
Step 2 - Data audit and GHG accounting is always the foundation. You cannot assess risk, set targets, or write disclosure language without a credible emissions inventory. The RAG-powered receipt parser in this step addresses the most operationally tedious part of inventory work: extracting structured data from unstructured documents like utility bills and energy invoices.
Steps 3 and 4 - Physical and transition risk are deliberately sequenced as companion pieces. Physical risk is asset-level and geospatial; transition risk is scenario-driven and financially oriented. They use different methodologies but produce a combined risk narrative that is the core analytical product of most climate engagements.
Step 5 - Double materiality builds on the risk work. The IRO register draws directly from the physical and transition risk findings, grounding the materiality assessment in the quantitative analysis rather than treating it as a separate qualitative exercise.
Step 6 - Disclosure is the capstone because it synthesizes everything. A credible IFRS S2 or CSRD disclosure cannot be written without the underlying inventory, risk assessment, and materiality determination already completed. Sequencing it last reflects how disclosure actually works in practice - it is the output of a process, not a starting point.

Three Prompts, Annotated
The following examples illustrate how the configuration shapes actual prompt-and-response interactions in this project.
Example 1 - GHG Calculation with Few-Shot Reasoning
Why it's structured this way: GHG calculations fail when AI tools hallucinate emission factors or drop unit conversions. Providing a worked example in the prompt (few-shot) before asking the model to process new data dramatically reduces these errors. The explicit citation requirement ensures every factor is traceable.
You are a GHG accounting analyst following the GHG Protocol Corporate Standard.

Here is a worked example:
- Input: 10,000 kWh of electricity consumed in the US in 2023
- Emission factor: 0.386 kg CO2e/kWh (EPA eGRID 2023, US average)
- Calculation: 10,000 × 0.386 = 3,860 kg CO2e = 3.86 tCO2e
- Confidence: High (primary activity data, published emission factor)

Now calculate emissions for the following:
- 45,000 kWh of electricity consumed in Germany in 2023
Return: emission factor used, source, calculation, result in tCO2e, confidence level.

Example 2 - Physical Risk Scoring with Chain of Thought
Why it's structured this way: Risk scores without rationale are not useful to clients or auditors. Requiring step-by-step reasoning forces the model to surface the assumptions behind each score, making outputs reviewable and defensible.
You are a physical climate risk analyst. Score the flood risk for the following asset
using a 1–5 scale. Reason through each step before giving a final score.

Asset: Manufacturing facility, Ho Chi Minh City, Vietnam
Scenario: SSP2-4.5, 2050 time horizon
Adaptive capacity: ND-GAIN Country Index score 43.2 (Vietnam, 2023)

Step 1 - Exposure: What is the projected change in flood frequency/intensity at this location?
Step 2 - Sensitivity: How sensitive is a manufacturing facility to flood disruption?
Step 3 - Adaptive capacity: What does the ND-GAIN score tell us about Vietnam's capacity to respond?
Step 4 - Score (1–5) with rationale
Step 5 - Confidence level and key uncertainties

Example 3 - IRO Identification for Double Materiality
Why it's structured this way: Most double materiality assessments identify topics rather than IROs, which is no longer sufficient under CSRD. This prompt forces the model to work at the IRO level - specifying whether each item is an impact, risk, or opportunity, where in the value chain it occurs, and which stakeholders are affected.
You are a sustainability analyst conducting a double materiality assessment
under CSRD ESRS E1 for a global manufacturing company.

For the topic of physical climate risk, identify all material IROs.
For each IRO return:
- Type: Impact / Risk / Opportunity
- Description (2 sentences maximum)
- Value chain position: Own operations / Upstream / Downstream
- Affected stakeholders
- Time horizon: Short (2025–2030) / Medium (2030–2040) / Long (2040–2050)
- Preliminary materiality: High / Medium / Low
- Dimension: Financial materiality / Impact materiality / Both

What This Makes Possible at Scale
A consultant working without this configuration can deliver one engagement at a time, rebuilding methodology from scratch on each project. With this configuration, the same analytical framework - the same scenario choices, scoring rubrics, output formats, and quality standards - can be applied consistently across every engagement.
This matters for three reasons.
First, consistency. When methodology is embedded in the configuration rather than held in the consultant's head, outputs are reproducible and auditable. A client or regulator can ask "how did you score this risk?" and the answer is documented.
Second, speed. Data extraction, emissions calculation, risk scoring across dozens of assets, and first-draft disclosure language can all be completed in a fraction of the time when the AI agent knows what methodology to apply and what format to return.
Third, quality floor. The configuration establishes a minimum standard that every output must meet: source citations on emission factors, rationale on every risk score, IRO-level granularity on materiality, framework alignment on disclosure language. Without the configuration, quality depends entirely on whether the consultant remembers to ask for these things on each individual prompt.
The goal is not to remove the consultant from the process. It is to ensure that when the consultant's judgment is needed, it is applied to the right problems.

Part of the AI-Augmented Sustainability & Climate Risk Portfolio | Taylor Black | github.com/taybeee/climate-portfolio
