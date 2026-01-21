**STRATEGIC INTENT**

Building memory-chat-v2.py

Phase 0.1 represents the first concrete step in a larger architectural transformation. The overarching goal is to extract CLI presentation logic from memory-chat.py into a reusable, professionally-designed package called `friday-cli`, while simultaneously preserving the existing codebase as stable integration test infrastructure.

This is not merely code reorganization. It's the beginning of a methodical decomposition of a monolithic application into modular, composable components that can evolve independently.

---

**PRIMARY OBJECTIVE: Establish CLI Display Infrastructure**

The core objective is to create `friday-cli/display.py` as a standalone module that provides rich, modern terminal output capabilities using the Rich library. This module will replace scattered `print()` statements throughout memory-chat.py with professionally formatted, visually consistent output.

**Why This Matters:**

Currently, memory-chat.py uses basic text output for everything from error messages to complex data structures. This creates several problems:

1. **Poor User Experience** - Plain text output is difficult to scan, lacks visual hierarchy, and provides no contextual cues about information importance
2. **Inconsistent Formatting** - Different parts of the codebase format similar information differently
3. **Limited Expressiveness** - Cannot easily display tables, progress indicators, or syntax-highlighted code
4. **Maintenance Burden** - Formatting logic is scattered across 3000+ lines, making it hard to maintain consistent styling

By extracting display logic into a dedicated module with Rich library integration, we gain:

1. **Professional Terminal UI** - Tables with borders, color-coded status indicators, syntax highlighting, progress spinners
2. **Consistency** - All output flows through well-defined functions with predictable formatting
3. **Maintainability** - Display logic centralized in ~300 lines instead of scattered across 3000
4. **Reusability** - Other applications (future friday-agent implementations) can use the same display infrastructure

---

**SECONDARY OBJECTIVE: Validate Incremental Extraction Pattern**

Phase 0.1 serves as a proof-of-concept for the entire Pre-Phase IV strategy. By successfully extracting display utilities, we validate that:

1. **Parallel Development Works** - memory-chat.py and memory-chat-v2.py can coexist without conflict
2. **Integration Points Are Clean** - The boundary between core logic and presentation is well-defined
3. **Testing Remains Intact** - memory-chat.py continues functioning as integration test infrastructure
4. **Risk Is Manageable** - We can extract functionality incrementally without breaking existing systems

If Phase 0.1 succeeds, it provides a template for Phases 0.2-0.4 (input handling, command registry, session management). If it reveals unexpected coupling or integration challenges, we learn those lessons early, before attempting more complex extractions.

---

**TERTIARY OBJECTIVE: Preserve Integration Test Infrastructure**

A critical constraint is that memory-chat.py must remain untouched and fully functional throughout this process. This is not optional—it's a hard requirement.

**Why This Constraint Exists:**

memory-chat.py currently serves dual purposes:
1. **Production Application** - It's the working implementation of Friday's memory system
2. **Integration Test Harness** - It validates that friday-memory components (ContextAssembler, PromptArchitect, MemoryController) work correctly together

If we modify memory-chat.py directly, we risk:
- Breaking ongoing memory system testing
- Introducing regressions that won't be caught until later
- Losing the ability to compare "before" and "after" behavior side-by-side

By creating memory-chat-v2.py instead, we maintain a stable baseline for comparison. If memory-chat-v2.py exhibits different behavior, we can immediately identify whether it's due to the CLI extraction or some other factor.

---

**CONCRETE DELIVERABLES**

**1. friday-cli Package Structure**

Create a new uv-managed Python package at:
```
/Users/chuckrussell/Dev/gendev/agent-framework/packages/friday-cli/
```

This package will have:
- Proper Python package structure (src layout)
- UV dependency management
- Rich library as primary dependency
- Clean module organization for future expansion

**2. display.py Module (~300 lines)**

Implement six categories of display functions:

**a) Help Display** - Transform plain text help into a Rich table with command descriptions, plus a panel showing usage tips (keyboard shortcuts, navigation hints)

**b) Tool Budget Display** - Create a comprehensive table showing tool execution statistics with circuit breaker states, color-coded by status (green=CLOSED, yellow=HALF_OPEN, red=OPEN), plus a summary panel with aggregate metrics

**c) Memory Statistics Display** - Multi-table output showing total entities, lifecycle distribution (episodic/working/semantic), context assembly performance metrics, and extraction statistics, all formatted as Rich panels and tables

**d) Error/Warning/Success Messages** - Standardized message formatting with icons (✗ for errors, ⚠ for warnings, ✓ for success, ℹ for info), color coding, and optional exception details with traceback support

**e) JSON/Code Display** - Syntax-highlighted output for JSON, Python, YAML, and other code formats using Rich's Syntax class with configurable themes and line numbers

**f) Progress Indicators** - Context managers for spinner animations during long operations and progress bars for operations with known duration

**3. memory-chat-v2.py (~500 lines)**

Create a refactored version of memory-chat.py that:
- Imports and uses friday-cli.display functions
- Maintains identical core logic (context assembly, LLM interaction, tool execution, memory extraction)
- Replaces all `print()` statements with appropriate display functions
- Preserves all command handlers and functionality
- Uses a simple input loop (will be replaced in Phase 0.4 with Prompt Toolkit)

**4. Validation Test Suite**

Document and execute a comprehensive test plan comparing memory-chat.py and memory-chat-v2.py:
- All commands produce functionally equivalent results
- Rich formatting displays correctly in terminal
- Error handling behaves identically
- Circuit breakers function the same way
- Memory extraction produces identical output

---

**SUCCESS CRITERIA**

Phase 0.1 is successful when:

1. **friday-cli package exists and installs cleanly** - Can be installed via UV and imported without errors
2. **All six display function categories are implemented** - Complete, documented, with proper type hints
3. **memory-chat.py remains unchanged** - Byte-for-byte identical to pre-Phase 0.1 version
4. **memory-chat-v2.py runs successfully** - Accepts input, processes commands, displays output using Rich
5. **Functional equivalence verified** - Side-by-side testing confirms identical behavior (different presentation, same results)
6. **Visual improvement demonstrated** - Rich formatting provides measurably better UX than plain text
7. **No performance regression** - memory-chat-v2.py responds as quickly as memory-chat.py
8. **Documentation complete** - README explaining package purpose, API documentation for display functions

---

**STRATEGIC VALUE BEYOND IMMEDIATE DELIVERABLES**

Phase 0.1 establishes patterns that will be replicated in subsequent phases:

**Dependency Management** - Demonstrates how to add modern Python libraries (Rich, later Prompt Toolkit and Click) to the Friday ecosystem

**Module Boundaries** - Proves that presentation logic can be cleanly separated from business logic

**Testing Strategy** - Validates the parallel-development approach for risk mitigation

**Code Quality** - Sets the bar for documentation, type hints, and API design in extracted modules

**Reusability** - Creates the first truly reusable Friday component that could be used by other applications

---

**RISK MITIGATION**

The dual-file approach (memory-chat.py + memory-chat-v2.py) mitigates several risks:

**Technical Risk** - If friday-cli integration breaks something, we can immediately compare against the working baseline

**Schedule Risk** - If Phase 0.1 takes longer than expected, memory-chat.py continues working for ongoing development

**Scope Risk** - If we discover display extraction is more complex than anticipated, we can adjust Phase 0.2-0.4 plans based on lessons learned

**Rollback Risk** - If memory-chat-v2.py proves problematic, we simply continue using memory-chat.py with zero disruption

---

**ALIGNMENT WITH BROADER VISION**

Phase 0.1 is the first step toward the ultimate goal: a modular Friday architecture where:

- `friday-cli` provides terminal interface
- `friday-agent` provides agent execution logic
- `friday-memory` provides memory management
- `friday-context` provides context assembly
- Applications like memory-chat-v2.py are thin orchestration layers (~200 lines) that compose these packages


Building memory-chat-v2.py


**Phase 0.1 Roadmap: CLI Display Infrastructure Extraction**

Based on PRD analysis and memory_chat.py inspection, here's the decomposition into Claude Code work units:

---

**Phase 0.1a: Core Display Functions (Week 1)**

**Unit 1.1: Package Bootstrap**
- Create friday-cli package structure under `/packages/friday-cli/`
- Configure UV dependency management (pyproject.toml)
- Add Rich library dependency
- Verify package installs cleanly

**Unit 1.2: Message Display Functions**
- Implement `display_error()` - Red ✗ icon, exception details optional
- Implement `display_warning()` - Yellow ⚠ icon
- Implement `display_success()` - Green ✓ icon  
- Implement `display_info()` - Blue ℹ icon
- Add type hints, docstrings

**Unit 1.3: Basic Integration Test**
- Create minimal test script importing friday-cli.display
- Verify all four message functions render correctly
- Document visual output

---

**Phase 0.1b: Structured Data Display (Week 2)**

**Unit 2.1: JSON/Code Syntax Highlighting**
- Implement `display_json()` using Rich Syntax class
- Implement `display_code()` with language detection (Python, YAML, etc.)
- Support line numbers, theme configuration

**Unit 2.2: Table Rendering**
- Implement `display_table()` for structured data
- Support column alignment, borders, headers
- Handle nested data structures

**Unit 2.3: Integration Test**
- Test JSON display with memory extraction output
- Test table display with entity/fact lists
- Verify readability improvement over plain text

---

**Phase 0.1c: Progress & Help Display (Week 3)**

**Unit 3.1: Progress Indicators**
- Implement `display_spinner()` context manager
- Implement `display_progress()` for operations with known duration
- Test with simulated long-running operations

**Unit 3.2: Help System**
- Implement `display_help()` using Rich panels and tables
- Format command descriptions, usage tips
- Add keyboard shortcuts panel

**Unit 3.3: Integration Test**
- Verify spinner displays during context assembly
- Verify help output matches memory_chat.py functionality
- Document visual improvements

---

**Phase 0.1d: Memory & Tool Statistics (Week 4)**

**Unit 4.1: Tool Budget Display**
- Implement `display_tool_budget()` 
- Multi-table layout: per-tool stats, circuit breaker states
- Color-code by status (green/yellow/red)
- Add aggregate metrics panel

**Unit 4.2: Memory Statistics Display**
- Implement `display_memory_stats()`
- Tables for: entity counts, lifecycle distribution, performance metrics
- Format using Rich panels

**Unit 4.3: Integration Test**
- Compare tool budget output: memory_chat.py vs friday-cli version
- Compare memory stats output: memory_chat.py vs friday-cli version
- Verify functional equivalence

---

**Phase 0.1e: memory-chat-v2.py Integration (Week 5)**

**Unit 5.1: Create memory-chat-v2.py Scaffold**
- Copy memory_chat.py to memory_chat-v2.py
- Add friday-cli import statements
- Preserve all core logic unchanged

**Unit 5.2: Replace Display Calls (Incremental)**
- Replace error/warning/success print() statements → display functions
- Replace JSON dumps → display_json()
- Replace help text → display_help()
- Replace tool budget output → display_tool_budget()
- Replace memory stats output → display_memory_stats()

**Unit 5.3: Validation Testing**
- Side-by-side execution: memory_chat.py vs memory_chat-v2.py
- Test all 30+ slash commands
- Verify functional equivalence
- Document visual improvements
- Performance comparison (no regression)

---

**Phase 0.1f: Documentation & Finalization (Week 6)**

**Unit 6.1: API Documentation**
- Document all display functions (parameters, return types, examples)
- Create friday-cli README
- Add usage examples

**Unit 6.2: Final Validation**
- Execute comprehensive test suite
- Verify success criteria (all 8 points from PRD)
- Document lessons learned for Phase 0.2-0.4

**Unit 6.3: Handoff**
- Tag release: friday-cli v0.1.0
- Archive validation test results
- Update project roadmap with Phase 0.2 adjustments based on learnings

---

**Total: 18 discrete work units across 6 weeks**

Each unit is sized for Claude Code completion (1-3 hours). Units within sub-phases can execute sequentially. Integration tests validate incremental progress.

**Critical Path:** Units 1.1 → 1.2 → 2.1 → 2.2 → 3.1 → 3.2 → 4.1 → 4.2 → 5.1 → 5.2 → 5.3

**Validation Gates:** End of each sub-phase (1.3, 2.3, 3.3, 4.3, 5.3, 6.2)



