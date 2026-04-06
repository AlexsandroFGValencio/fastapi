---
description: description: Generate technical specifications (SDD-SPEC) for new features following the Software Design Document defined in docs/constitution.md 
---

# SDD-SPEC: Specification Generation Workflow

## Purpose

This workflow guides the process of creating technical specifications (specs) following the Software Design Document (SDD) defined in `docs/constitution.md`.

---

## Step 1: Read Constitution First

**Before starting ANY analysis, you MUST:**

1. Read the entire `docs/constitution.md` file
2. Understand and internalize ALL rules defined in the constitution
3. Every decision in the spec MUST comply with the constitution rules

The constitution contains:
- Hexagonal Architecture rules (MUST be followed)
- SOLID, YAGNI, KISS, DRY principles (MUST be applied)
- Security requirements (OWASP Top 10)
- Testing requirements (100% coverage)
- Performance SLOs (P95 ≤ 504ms, P99 ≤ 1000ms)
- Naming conventions
- Code reuse guidelines

**All rules marked as MUST in the constitution are mandatory and non-negotiable.**

---

## Step 2: Receive the Card

Wait for the user to paste the card content (user story, requirement, or feature description).

---

## Step 3: Initial Analysis

After receiving the card, you **MUST**:

1. Read and fully understand the requirement
2. Cross-reference with constitution.md rules
3. Identify all points that need clarification
4. List required dependencies and integrations
5. Check for conflicts with existing functionality

---

## Step 4: Questioning Phase

You **MUST NOT** assume any premise. For each unclear point, ask specific questions.

**Mandatory question categories:**

### 4.1 Scope and Functionality
- What is the expected behavior in each scenario?
- Are there edge cases that need to be handled?
- What is the behavior in case of error?

### 4.2 Architecture
- Which layer of the hexagonal architecture does this feature fit into?
- Are there adapters, ports, or use cases that can be reused?
- Is it necessary to create new components?

### 4.3 Integrations
- Which external services will be consumed?
- What is the expected contract (request/response)?
- What is the timeout and fallback strategy?

### 4.4 Performance
- What is the maximum acceptable latency?
- What is the expected request volume?
- Is cache needed? If so, what TTL?

### 4.5 Data
- Which fields are required vs optional?
- What validations are needed?
- Are there data transformations?

### 4.6 Security
- Which authorization scopes are required?
- Is there sensitive data involved?
- Is specific rate limiting needed?

### 4.7 Versioning and Compatibility
- Is this a breaking change?
- Does it affect the existing API contract?
- Is a feature flag needed for gradual rollout?

### 4.8 Search API Specific Questions

**Query and Relevance:**
- Does this feature affect the  query structure?
- Is boosting required? If so, what type (SKU, brand, category, recommendation)?
- Does it affect the relevance score calculation?
- Should results be sorted differently? By what criteria?
- Does it require changes to the `function_score` query?

**Filters and Facets:**
- Does this add a new filter to the search?
- Should this filter be a `must`, `should`, or `must_not` clause?
- Does it require a new facet/aggregation?
- How should the filter interact with existing filters (AND/OR)?

**Index and Data:**
- Which  index fields are involved?
- Is the field already indexed? If not, is reindexing needed?
- Does it affect multiple business units (BOT, EUD, OUI, QDB)?
- Does it require changes to the index mapping?

**Boosting and Personalization:**
- Does it involve personalized recommendations?
- Should results with this feature be cached? (personalized results MUST NOT be cached)
- Does it require integration with the Recommendation API?
- What is the boost weight/priority?

**Inventory and Availability:**
- Does it interact with inventory filters?
- Should it consider distribution center availability?
- How should out-of-stock products be handled?

**Circuit Breaker and Resilience:**
- Does it depend on an external service?
- What is the fallback behavior if the service fails?
- Should it use the existing circuit breaker or need a new one?

---

## Step 5: Iteration

Repeat the questioning phase **as many times as necessary** until:
- All points are clear
- There are no ambiguities
- The scope is well defined

---

## Step 6: Spec Generation

After all doubts are clarified, generate the specification in the following format:

```markdown
# Spec: [Feature Name]

## 1. Overview

### 1.1 Objective
[Clear description of what will be implemented]

### 1.2 Scope
- Included: [list]
- Excluded: [list]

### 1.3 References
- Card: [link or ID]
- Constitution: docs/constitution.md

---

## 2. Functional Requirements

### FR-001: [Name]
**Description:** [detailed description]
**Acceptance Criteria:**
- [ ] [criterion 1]
- [ ] [criterion 2]

---

## 3. Non-Functional Requirements

### NFR-001: Performance
- Latency P95: [value]
- Latency P99: [value]

### NFR-002: Availability
- SLO: [value]

### NFR-003: Security
- Authentication: [type]
- Authorization: [scopes]

---

## 4. Architecture

### 4.1 Component Diagram
[ASCII diagram or description]

### 4.2 Affected Layers

| Layer | Component | Action |
|-------|-----------|--------|
| Inbound Adapter | [name] | Create/Modify |
| Port | [name] | Create/Modify |
| Use Case | [name] | Create/Modify |
| Outbound Port | [name] | Create/Modify |
| Outbound Adapter | [name] | Create/Modify |

### 4.3 Code Reuse

| Existing Component | Location | Usage |
|-------------------|----------|-------|
| [name] | [path] | [how it will be used] |

---

## 5. API Contract

### 5.1 Endpoint
```
[METHOD] /v1/[path]
```

### 5.2 Request
```json
{
  "field": "type | required/optional | description"
}
```

### 5.3 Response
```json
{
  "field": "type | description"
}
```

### 5.4 Error Codes
| Code | Description | When |
|------|-------------|------|
| 400 | Bad Request | [scenario] |
| 401 | Unauthorized | [scenario] |
| 404 | Not Found | [scenario] |

---

## 6. Cache and Performance

### 6.1 Cache Strategy
- Cache enabled: Yes/No
- TTL: [value]
- Key: [format]

### 6.2 Timeouts
| Component | Timeout |
|-----------|---------|
| [name] | [value] |

---

## 7. Tests

### 7.1 Unit Test Scenarios
- [ ] [scenario 1]
- [ ] [scenario 2]

### 7.2 Integration Test Scenarios
- [ ] [scenario 1]

### 7.3 Edge Case Scenarios
- [ ] [scenario 1]

### 7.4 Security Test Scenarios
- [ ] [scenario 1]

---

## 8. Rollout

### 8.1 Feature Flag
- Name: [flag_name]
- Default behavior: [value]

### 8.2 Rollout Plan
1. [step 1]
2. [step 2]

---

## 9. Validation Checklist

- [ ] Hexagonal architecture respected
- [ ] SOLID principles applied
- [ ] YAGNI: no speculative code
- [ ] KISS: simplest solution
- [ ] DRY: code reused
- [ ] Performance within SLOs
- [ ] OWASP security verified
- [ ] Tests planned (100% coverage)
- [ ] Versioning considered
- [ ] Feature flag defined (if applicable)
```

---

## Step 7: Final Validation

Before finishing, confirm with the user:

1. Is the spec complete and correct?
2. Were all requirements captured?
3. Is the architecture adequate?
4. Are the test scenarios complete?

---

## Usage Example

**User:** [pastes the card]

**AI:** 
"I analyzed the card. I have the following questions before generating the spec:

1. **Scope:** The card mentions 'filter by category', but doesn't specify if it's single or multi-select. What is the expected behavior?

2. **Performance:** What is the maximum acceptable latency for this search?

3. **Cache:** Should results be cached? If so, for how long?

..."

**User:** [answers the questions]

**AI:** [asks more questions if needed or generates the spec]

---

## Language

Always interact with the user in Portuguese (Brazilian).
