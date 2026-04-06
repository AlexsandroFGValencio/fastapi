---
description: description: Implement code following validated technical specifications (SDD-CODE) and the Software Design Document defined in docs/constitution.md
---

# SDD-CODE: Code Implementation Workflow

## Purpose

This workflow guides the code implementation process following a validated spec and the Software Design Document (SDD) defined in `docs/constitution.md`.

---

## Step 1: Read Constitution First

**Before starting ANY implementation, you MUST:**

1. **Read the entire `docs/constitution.md` file**
2. **Understand and internalize ALL rules defined in the constitution**
3. **Every line of code MUST comply with the constitution rules**

**All rules marked as MUST in the constitution are mandatory and non-negotiable.**

---

## Step 2: Receive the Spec

Wait for the user to provide the name or path of the validated spec.

**Example:**
- "Implement spec: filter-by-category"
- "Implement docs/specs/FR-001-new-endpoint.md"

---

## Step 3: Spec Analysis

After receiving the spec, you **MUST**:

1. Read the spec completely
2. Identify all components to be created/modified
3. Check existing code that can be reused
4. Map the implementation to the hexagonal architecture

---

## Step 4: Reuse Verification

Before creating any new code, you **MUST** check:

```
src/search_api/
├── domain/
│   ├── entities/          # Existing entities
│   ├── ports/
│   │   ├── inbound/       # Existing inbound ports
│   │   └── outbound/      # Existing outbound ports
│   └── use_cases/         # Existing use cases
│       └── helpers/       # Reusable helpers
├── adapters/
│   ├── inbound/           # Inbound adapters
│   └── outbound/          # Outbound adapters
│       └── helpers/       # Adapter helpers
└── core/
    └── factories/         # Existing factories
```

---

## Step 5: Implementation Order

Follow **mandatorily** this order (from inside out):

```
1. Domain Layer (Core)
   ├── 1.1 Entities (if needed)
   ├── 1.2 DTOs
   ├── 1.3 Ports (Interfaces)
   └── 1.4 Use Cases

2. Adapters Layer
   ├── 2.1 Outbound Adapters (outbound port implementations)
   └── 2.2 Inbound Adapters (controllers, etc.)

3. Infrastructure
   ├── 3.1 Factories
   └── 3.2 Configurations
```

---

## Step 6: Implementation Rules

### 6.1 Hexagonal Architecture

- Domain layer **MUST NOT** import from adapters
- Use Cases **MUST** receive Ports via dependency injection
- Adapters **MUST** implement Ports defined in domain

### 6.2 Code

- Type hints **MUST** be used in all code
- Functions **SHOULD NOT** exceed 30 lines
- Cyclomatic complexity **MUST NOT** exceed 8
- Duplicated code **MUST** be extracted to helpers

### 6.3 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `SearchProductUseCase` |
| Functions/Methods | snake_case | `get_all_boosts` |
| Variables | snake_case | `search_filter` |
| Constants | UPPER_SNAKE_CASE | `TIMEOUT_ERROR_MESSAGE` |
| Ports | PascalCase + Port | `SearchRepositoryPort` |
| Adapters | PascalCase + Adapter | `8RepositoryAdapter` |
| DTOs | PascalCase + DTO | `SearchFilterDTO` |

### 6.4 Security

- Authentication **MUST** use `get_current_user`
- Authorization **MUST** use appropriate scopes
- Input validation **MUST** use Pydantic
- Credentials **MUST NOT** be hardcoded

---

## Step 7: Test Generation

For each created component, you **MUST** create tests with **100% coverage**.

### 7.1 Test Structure

```
tests/search_api/
├── adapters/
│   ├── inbound/
│   │   └── rest/v1/controllers/
│   │       └── test_[controller].py
│   └── outbound/
│       └── [adapter]/
│           └── test_[adapter].py
├── domain/
│   ├── entities/
│   │   └── test_[entity].py
│   └── use_cases/
│       └── test_[use_case].py
└── conftest.py  # Shared fixtures
```

### 7.2 Mandatory Test Types

For each component:

1. **Happy Path** - Success scenario
2. **Edge Cases** - Boundary values, empty lists, None
3. **Error Cases** - Exceptions, timeouts, failures
4. **Security Cases** - Injection, XSS, authentication

### 7.3 Test Pattern

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
class TestClassName:
    """Tests for ClassName."""

    @pytest.fixture
    def sut(self) -> ClassName:
        """System Under Test."""
        return ClassName(
            dependency=AsyncMock(spec=DependencyPort),
        )

    async def test_method_when_scenario_should_result(self, sut: ClassName):
        """Tests [scenario description]."""
        input_data = ...

        result = await sut.method(data=input_data)

        assert result == expected

    async def test_method_when_error_should_raise_exception(self, sut: ClassName):
        """Tests behavior in case of error."""
        sut.dependency.method.side_effect = SomeException()

        with pytest.raises(ExpectedException):
            await sut.method(data=input_data)
```

---

## Step 8: Execution and Validation

After implementing all code and tests:

### 8.1 Run Tests

```bash
make test
```

### 8.2 If Tests Fail

1. Analyze the error
2. Fix the code (not the test, unless the test is wrong)
3. Run again
4. Repeat until all tests pass

### 8.3 Check Coverage

```bash
make test-coverage
```

- Coverage **MUST** be 100% for new code

### 8.4 Run Lint

```bash
make lint
```

- Lint **MUST** pass without errors

---

## Step 9: Final Checklist

Before finishing, verify:

- [ ] Code **MUST** follow naming conventions
- [ ] Type hints **MUST** be in all functions/methods
- [ ] Tests **MUST** have 100% coverage
- [ ] Edge cases **MUST** be tested
- [ ] Security tests **MUST** be implemented
- [ ] Lint **MUST** pass (`make lint`)
- [ ] SOLID principles **MUST** be respected
- [ ] YAGNI: speculative code **MUST NOT** be added
- [ ] KISS: solution **SHOULD** be the simplest possible
- [ ] All tests **MUST** pass (`make test`)

---

## Step 10: Deliverables

When finished, list:

1. **Files Created:**
   - `path/to/file.py` - Description

2. **Files Modified:**
   - `path/to/file.py` - What was changed

3. **Tests Created:**
   - `tests/path/to/test_file.py` - Scenario coverage

4. **Commands Executed:**
   - `make test` - Status: ✅ Passed
   - `make lint` - Status: ✅ Passed

---

## Usage Example

**User:** "Implement spec: docs/specs/filter-by-rating.md"

**AI:**
"I analyzed the spec 'filter-by-rating'. I will implement the following components:

**1. Domain Layer:**
- DTO: `RatingFilterDTO` in `domain/ports/inbound/search/dtos.py`
- Port: Update `SearchRepositoryPort` (already exists)
- Use Case: Update `SearchProductUseCase` (already exists)

**2. Adapters Layer:**
- Query Builder: `build_rating_filter()` in `adapters/outbound/_8/queries_builder/`
- Controller: Update `V1SearchParams` (already exists)

**3. Tests:**
- `tests/search_api/adapters/outbound/_8/queries_builder/test_rating.py`
- Update `tests/search_api/domain/use_cases/test_search_product.py`

Starting implementation..."

[Implements code]

"Running `make test`..."

[If it fails, fixes and runs again]

"✅ Implementation completed:

**Files Created:**
- `src/search_api/adapters/outbound/_8/queries_builder/rating.py`
- `tests/search_api/adapters/outbound/_8/queries_builder/test_rating.py`

**Files Modified:**
- `src/search_api/domain/ports/inbound/search/dtos.py` - Added field `rating_min`
- `src/search_api/adapters/inbound/rest/v1/params/search.py` - Added parameter

**Commands:**
- `make test` - ✅ Passed (245 tests)
- `make lint` - ✅ Passed"

---

## Summary Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      SDD-CODE FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Receive Spec                                                │
│     └── Read and analyze validated spec                        │
│                                                                 │
│  2. Verify Reuse                                                │
│     └── Search for existing code                               │
│                                                                 │
│  3. Implement (from inside out)                                 │
│     ├── Domain Layer (entities, DTOs, ports, use cases)        │
│     ├── Adapters Layer (outbound, inbound)                     │
│     └── Infrastructure (factories, config)                     │
│                                                                 │
│  4. Create Tests (100% coverage)                                │
│     ├── Happy path                                              │
│     ├── Edge cases                                              │
│     ├── Error cases                                             │
│     └── Security cases                                          │
│                                                                 │
│  5. Execute and Validate                                        │
│     ├── make test (repeat until pass)                          │
│     ├── make test-coverage (verify 100%)                       │
│     └── make lint (must pass)                                  │
│                                                                 │
│  6. Deliver                                                     │
│     └── List created/modified files                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Language

Always interact with the user in Portuguese (Brazilian).
