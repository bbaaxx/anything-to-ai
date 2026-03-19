# Data Model: Test Cleanup and Quality Assurance

## Test Suite Entity

**TestSuite**
- id: string (unique identifier)
- name: string (descriptive name)
- status: enum (passing, failing, flaky, quarantined)
- coverage_percentage: float (0-100)
- last_run: timestamp
- test_count: integer
- failure_count: integer
- flaky_count: integer

## Quality Report Entity

**QualityReport**
- id: string (unique identifier)
- module_name: string (source module)
- violation_count: integer
- complexity_score: float
- maintainability_index: float
- last_check: timestamp
- violations: array of QualityViolation

## Quality Violation Entity

**QualityViolation**
- rule_code: string (ruff rule identifier)
- severity: enum (error, warning, info)
- line_number: integer
- column_number: integer
- message: string (description of violation)
- file_path: string (absolute path to file)

## Test Result Entity

**TestResult**
- test_id: string (unique identifier)
- test_name: string
- status: enum (passed, failed, skipped, error)
- execution_time: float (seconds)
- failure_message: string (if failed)
- file_path: string
- line_number: integer
- is_flaky: boolean

## Coverage Data Entity

**CoverageData**
- module_name: string
- total_lines: integer
- covered_lines: integer
- uncovered_lines: array of integers
- coverage_percentage: float
- last_measured: timestamp

## Relationships

- TestSuite 1..* TestResult (one suite has many test results)
- QualityReport 1..* QualityViolation (one report has many violations)
- CoverageData belongs to TestSuite (coverage for each module in suite)

## Validation Rules

- coverage_percentage must be >= 80.0 for passing status
- complexity_score must be <= 10.0 for acceptable quality
- maintainability_index must be >= 70.0 for acceptable quality
- flaky tests must be marked with quarantine marker
- all fixes must not increase total violation count
