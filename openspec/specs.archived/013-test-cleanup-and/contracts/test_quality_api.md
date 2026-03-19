# Test Quality API Contracts

## Test Suite Management

### GET /api/test/suites
**Description**: Retrieve all test suites with their status and coverage
**Response**:
```json
{
  "suites": [
    {
      "id": "string",
      "name": "string",
      "status": "passing|failing|flaky|quarantined",
      "coverage_percentage": "float",
      "last_run": "timestamp",
      "test_count": "integer",
      "failure_count": "integer",
      "flaky_count": "integer"
    }
  ]
}
```

### POST /api/test/suites/{suite_id}/run
**Description**: Execute a specific test suite
**Response**:
```json
{
  "suite_id": "string",
  "status": "running|completed|failed",
  "started_at": "timestamp",
  "results": "TestResult[]"
}
```

### POST /api/test/suites/{suite_id}/quarantine
**Description**: Quarantine flaky tests in a suite
**Request**:
```json
{
  "test_ids": ["string"]
}
```

## Quality Check Management

### GET /api/quality/reports
**Description**: Retrieve quality reports for all modules
**Response**:
```json
{
  "reports": [
    {
      "id": "string",
      "module_name": "string",
      "violation_count": "integer",
      "complexity_score": "float",
      "maintainability_index": "float",
      "last_check": "timestamp",
      "violations": "QualityViolation[]"
    }
  ]
}
```

### POST /api/quality/check
**Description**: Run quality checks on specified modules
**Request**:
```json
{
  "modules": ["string"]
}
```

### POST /api/quality/fix
**Description**: Apply atomic fixes to quality violations
**Request**:
```json
{
  "violations": [
    {
      "file_path": "string",
      "line_number": "integer",
      "rule_code": "string"
    }
  ]
}
```

## Coverage Management

### GET /api/coverage/modules
**Description**: Retrieve coverage data for all modules
**Response**:
```json
{
  "modules": [
    {
      "module_name": "string",
      "total_lines": "integer",
      "covered_lines": "integer",
      "uncovered_lines": ["integer"],
      "coverage_percentage": "float",
      "last_measured": "timestamp"
    }
  ]
}
```

### POST /api/coverage/measure
**Description**: Measure test coverage for specified modules
**Request**:
```json
{
  "modules": ["string"]
}
```
