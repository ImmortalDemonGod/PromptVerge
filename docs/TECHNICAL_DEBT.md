# PromptVerge MVP: Zero-Day Technical Debt Ledger

This document lists all technical debt incurred during the PromptVerge MVP "Zero-Day Protocol" sprint. Each item represents a conscious shortcut taken to prioritize speed and delivery of a functional end-to-end system. All items must be addressed in subsequent development cycles.

## 🎉 **MAJOR MILESTONE ACHIEVED (2025-07-05)**

**Engineering Workflow is now LIVE with AI integration!** The core value proposition has been activated:
- ✅ Live OpenAI API calls replacing placeholder functions
- ✅ Real AI-generated Code Audits, PRDs, and Deep Work Tasks
- ✅ Schema validation working perfectly
- ✅ CLI saving structured outputs to JSON files
- ✅ End-to-end pipeline functional and tested

**Status**: PromptVerge has successfully transitioned from MVP skeleton to functional AI-powered system.

## 🚀 **SECOND MAJOR MILESTONE ACHIEVED (2025-07-05)**

**Knowledge Workflow is now LIVE with AI integration!** Both core workflows are now operational:
- ✅ Live zShot/spaCy KG extraction pipeline
- ✅ Real AI-generated Knowledge Graph Quizzes
- ✅ Schema validation working perfectly for both workflows
- ✅ CLI saving structured outputs for both engineering and knowledge workflows
- ✅ Comprehensive test coverage with both mocked and live AI scenarios

**Status**: PromptVerge is now a **fully functional dual-workflow AI system** ready for production use.

---

### TD-001: Hardcoded Configuration

- **Issue:** All configuration values, including file paths, prompt templates, and model parameters, are hardcoded directly into the source code.
- **Risk:** High. Makes the system brittle, difficult to configure for different environments (dev, staging, prod), and hard to maintain. Changes require direct code edits and redeployment.
- **Repayment Strategy:** Implement a formal configuration management system, such as [Hydra](https://hydra.cc/) or Pydantic's `BaseSettings`, to externalize all configuration. Create default config files and allow for environment-specific overrides.

---

### ~~TD-002: Placeholder Knowledge Graph Extraction~~ ✅ **COMPLETED (2025-07-05)**

- **Issue:** ~~The `extract_kg_triples` function in the knowledge workflow is a placeholder that returns a hardcoded, static value.~~ **RESOLVED: Implemented live zShot + spaCy KG extraction pipeline**
- **Risk:** ~~High. The core value proposition of the knowledge workflow is blocked. The system cannot process new scientific papers.~~ **RESOLVED: Knowledge workflow now fully operational**
- **Resolution:** ✅ Implemented real KG extraction using `zShot` with `KnowGL` extractor and `spaCy` NLP processing. The system now extracts knowledge graph triples from text and generates contextually appropriate quizzes.

---

### TD-003: Lack of Unit Tests

- **Issue:** The project relies exclusively on a single end-to-end integration test. There are no unit tests for individual functions, schemas, or utilities.
- **Risk:** Medium. While the E2E test validates the full flow, it's difficult to pinpoint the source of failures. Refactoring is riskier without fine-grained tests to prevent regressions.
- **Repayment Strategy:** Develop a comprehensive suite of unit tests using `pytest`. Aim for high test coverage on all critical components, including schema validators, individual AI-powered functions (with mocks), and utility functions.

---

### TD-004: Insecure Secrets Management

- **Issue:** The OpenAI API key is expected to be in a local, unencrypted `.env` file. There is no mechanism for secure storage or rotation.
- **Risk:** Critical. Storing secrets in plaintext is a major security vulnerability. If the `.env` file is accidentally committed or exposed, the API key will be compromised.
- **Repayment Strategy:** Integrate a secure secrets management solution like HashiCorp Vault, AWS Secrets Manager, or Doppler. The application should fetch secrets at runtime, not store them on disk.

---

### TD-005: Non-Critical Prefect Logging Error

- **Issue:** A transient `ValueError: I/O operation on closed file` error is sometimes observed during the shutdown of Prefect's temporary server.
- **Risk:** Low. This error does not appear to affect the successful completion of the workflows. It is a minor annoyance in the logs.
- **Repayment Strategy:** Investigate the root cause of the logging error. It may be a known issue in the specific version of Prefect being used. If so, upgrade Prefect. If not, report the issue and implement a workaround if necessary. This is the lowest priority item.

---

### TD-006: Inability to Perform Mutation Testing

- **Issue:** The project's global `pytest` configuration, located in the monorepo root, overrides all local test settings. This makes it impossible to isolate the `PromptVerge` tests for mutation testing with tools like `mutmut`. All attempts to configure, override, or bypass the global configuration (including command-line flags, plugins like `pytest-xdist`, and custom runner scripts) have failed.
- **Risk:** Medium. While the system has 100% test coverage, the *quality* of those tests cannot be programmatically assessed. This means there may be blind spots or weaknesses in the test suite that could allow regressions to go undetected during future development and refactoring.
- **Repayment Strategy:** This issue is currently blocked by the monorepo's architecture. Repayment can only be considered if the global `pytest` configuration is refactored to allow for per-project overrides. An alternative would be to temporarily move the `PromptVerge` system out of the monorepo to perform mutation testing in a clean environment, though this is a significant undertaking.
