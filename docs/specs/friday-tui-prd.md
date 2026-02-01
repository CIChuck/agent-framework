# Product Requirements Document: Friday TUI (Terminal User Interface)

## 1. Executive Summary
The goal of this project is to develop a robust Terminal User Interface (TUI) for the Friday Framework, utilizing the `Textual` library. This TUI will serve as a rich, interactive frontend for the Friday Integration Test Application, providing a superior user experience compared to the existing raw CLI implementation. It will reside in a new dedicated package (`packages/friday-tui`) and aim for feature parity with the existing CLI tool (`tests/integration/memory/friday.py`).

## 2. Goals & Objectives
-   **Enhanced UX:** Provide a modern, windowed terminal interface with scrollable content, distinct areas for output/input, and status monitoring.
-   **Feature Parity:** Support all existing commands and workflows available in the `friday.py` CLI integration test.
-   **Modular Architecture:** Decouple the UI from the core chat/session logic to allow reusable components.
-   **Content-Aware Rendering:** Intelligently render content (Markdown, Code, Logs) for better readability.

## 3. Scope
### 3.1. In Scope
-   Creation of a new package: `packages/friday-tui`.
-   Refactoring of core session logic (currently in `tests/integration/memory/friday.py` and `friday_chat`) into a shared library to be accessible by the TUI package.
-   Implementation of the TUI layout using `Textual`:
    -   **Workspace (Left):** File/Context tree (initial placeholder/basic implementation).
    -   **Scrollable Content (Top Right):** Main interaction area displaying conversation history and command outputs.
    -   **Prompt Area (Middle Right):** User input field.
    -   **Status Area (Bottom):** Logs, errors, warnings, and debug info.
-   Integration of the TUI into a new integration test entry point (`tests/integration/tui/main.py`).

### 3.2. Out of Scope (Phase 1)
-   Full implementation of the Workspace features (e.g., full file management) beyond basic directory viewing.
-   Mouse support (focus is on keyboard-first, though Textual supports mouse).
-   GUI or Web interface.

## 4. User Interface Specification
The TUI layout consists of a grid structure:

```
+---------------------+------------------------------------------+
|                     |                                          |
|                     |           Scrollable Content             |
|                     |       (Markdown, Chat History)           |
|      Workspace      |                                          |
|   (Tree Structure)  |                                          |
|                     |                                          |
|                     +------------------------------------------+
|                     |           Prompt Area (Input)            |
|                     +------------------------------------------+
|                     |     Status Area (Errors/Warnings)        |
+---------------------+------------------------------------------+
```

### 4.1. Components
1.  **Workspace (Sidebar)**
    -   **Widget:** `DirectoryTree` or custom Tree.
    -   **Purpose:** Show current working directory context.
    -   **Future:** Context management, drag-and-drop support.

2.  **Scrollable Content (Main View)**
    -   **Widget:** `RichLog` or `VerticalScroll` containing `Markdown` widgets.
    -   **Behavior:** Auto-scroll to bottom on new content. Support standard Markdown rendering (bold, italics, code blocks, tables).
    -   **Content-Awareness:** Distinguish between:
        -   User Prompts (e.g., colored prefix `Chuck: >`).
        -   System Responses (Markdown rendered).
        -   Command Output (Tables, Logs).

3.  **Prompt Area**
    -   **Widget:** `Input`.
    -   **Behavior:** Accepts user text. Supports history navigation (Up/Down arrows). Submits on Enter.

4.  **Status Area**
    -   **Widget:** `RichLog` or `Log`.
    -   **Behavior:** Displays transient errors, warnings, and background maintenance logs (e.g., "Incremental maintenance: merged...").

## 5. Technical Architecture

### 5.1. Package Structure
The solution requires creating a new package and refactoring existing logic to avoid code duplication and circular dependencies.

**New Package:** `packages/friday-tui/`
```
packages/friday-tui/
├── pyproject.toml       # Dependencies: textual, friday-core, friday-chat (refactored)
├── src/
│   └── friday_tui/
│       ├── __init__.py
│       ├── app.py       # Main App(App) class
│       ├── screens.py   # MainScreen definition
│       ├── widgets.py   # Custom widgets (ChatLog, StatusLog)
│       └── controller.py # Bridge to MemoryChatSession
```

**Shared Logic Refactoring:**
The `MemoryChatSession` class and `friday_chat` module currently live in `tests/integration/memory/`. These **MUST** be moved to a shared package to be importable by `friday-tui`.
-   **Proposal:** Promote `tests/integration/memory/friday_chat` to `packages/friday-chat`.
-   **Action:** Move `MemoryChatSession` logic from `tests/integration/memory/friday.py` into `packages/friday-chat/src/friday_chat/session.py`.

### 5.2. Integration Logic
-   The TUI App will instantiate `MemoryChatSession` (from the refactored package).
-   **Event Loop:** Textual runs its own async event loop. `MemoryChatSession` methods should be async.
-   **Output Redirection:**
    -   The current `MemoryChatSession` uses `friday_cli` display functions (e.g., `display_error`, `display_table`).
    -   **Challenge:** These functions print directly to stdout/stderr using `rich.console`.
    -   **Solution:**
        1.  **Dependency Injection:** Refactor `MemoryChatSession` to accept a `DisplayInterface`.
        2.  **Adapter:** Implement a `TextualDisplayAdapter` in `friday-tui` that implements this interface and routes output to the appropriate Textual widgets (ChatLog vs StatusLog).
        3.  **Events:** Alternatively, `MemoryChatSession` can emit events/signals that the TUI listens to.

### 5.3. Dependencies
-   `textual >= 0.50.0`
-   `friday-core`
-   `friday-chat` (new/refactored package)

## 6. Functional Requirements
1.  **Startup:**
    -   Initialize `MemoryChatSession` with configuration (config.yaml).
    -   Load existing context/memory.
2.  **Command Handling:**
    -   Intercept `/` commands in the Input widget.
    -   Route to `MemoryChatSession.handle_command`.
    -   Display result in ChatLog.
3.  **Chat Interaction:**
    -   Send user input to `MemoryChatSession`.
    -   Display streaming response (if supported) or final response in ChatLog.
4.  **UI Controls:**
    -   `Ctrl+C` or `/exit`: Quit application.
    -   `Ctrl+L`: Clear screen (ChatLog).
    -   Scrolling keys for Content/Status areas.

## 7. Build & Migration Plan
1.  **Refactor:** Extract `friday_chat` and `MemoryChatSession` from `tests/` to `packages/friday-chat`.
2.  **Scaffold:** Create `packages/friday-tui` with `pyproject.toml`.
3.  **Implement:** Build the `Textual` app with the specified layout.
4.  **Bridge:** Connect the TUI input/output to the `MemoryChatSession`.
5.  **Test:** Create `tests/integration/tui/main.py` that launches the TUI.
6.  **Verify:** Ensure all `/commands` (history, context, memory, tools) function correctly in the new interface.

## 8. Open Questions / Risks
-   **Streaming Output:** How does `MemoryChatSession` handle streaming tokens from the LLM? If it uses a callback or yields, the TUI needs to handle this update loop efficiently to update the Markdown widget in real-time.
-   **Rich Console Conflicts:** Existing `friday-cli` tools might hardcode `Console()`. We need to ensure they don't corrupt the Textual display. (Textual manages the terminal exclusively). *Mitigation:* Ensure `friday-cli` functions allow passing a `Console` instance or capture output to strings before rendering in Textual.
