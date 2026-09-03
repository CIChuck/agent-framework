# Product Requirement Document: Friday OS (V2)

## 1. Executive Summary

**Friday** has evolved from a framework into a persistent, autonomous **AI Operating System**.

This PRD defines the architecture for **`packages/friday-os`**, the infrastructure package that acts as the runtime environment. It provides the **Substrate** (Scheduler, Event Bus, Concurrency Control) and the **Safety Kernel** upon which the **Friday Application** (`apps/friday-cli`) runs.

The architecture separates the **Infrastructure** (process management, safety, memory integrity) from the **Application Logic** (personalities, specific prompts, user interaction).

## 2. Naming & Package Structure

### 2.1 `packages/friday-os` (The Infrastructure)
*   **Role:** The Kernel / Runtime.
*   **Responsibility:** Manages the **Dual-State Runtime** (Day/Night) and the **Persistent Sentinel Layer**. Enforces safety policies, manages database locks, and routes events.
*   **Analogy:** This is "Linux". It manages resources and safety so agents can run.

### 2.2 `apps/friday-cli` (The Application)
*   **Command:** `friday`
*   **Role:** The User Experience.
*   **Responsibility:** Instantiates the OS, configures the specific Agents (Chat, Janitor), connects the TUI (Textual/Rich), and handles user input.
*   **Analogy:** This is the "Desktop Environment" or "Shell".

## 3. Core Vision: The Runtime Model

The OS consists of a **Persistent Supervisor** (Sentinel) wrapping a **Dual-State Runtime**.

### 3.1 The Persistent Sentinel Layer (Always On)
*   **Status:** Parallel Process / Sidecar.
*   **Primary Agent:** **Sentinel Agent** (Supervisor/Dispatcher).
*   **Responsibility:**
    *   **Observability:** Monitors System Health (RAM/CPU), External Triggers (Web/Stocks), and Internal Task Status.
    *   **Dispatcher:** Manages the Event Bus. Decides *how* to interrupt the current Runtime State (e.g., inject alert into Chat vs. log to Morning Report).
*   **Safety Profile:** **Mission Critical**. If this crashes, the OS restarts.

### 3.2 Runtime State A: Day Mode (Active/Interactive)
*   **Status:** Mutually Exclusive with Night Mode.
*   **Trigger:** User Input / Presence.
*   **Primary Agent:** **Chat Agent** (`InteractiveAgent`).
*   **Behavior:** Serves user requests. Queues maintenance tasks.
*   **Safety Profile:** **Lenient**. Warn user on loops, allow override.

### 3.3 Runtime State B: Night Mode (Sleep/Dream)
*   **Status:** Mutually Exclusive with Day Mode.
*   **Trigger:** `/sleep` command or Inactivity Timeout.
*   **Primary Agent:** **Janitor Agent** (`AutonomousAgent`).
*   **Behavior:** Consolidation, Refactoring, Deep Work.
*   **Safety Profile:** **Strict**. Hard stop on loops. Max 2 retries.

## 4. System Architecture

### 4.1 The Safety Kernel (The Immune System)
A middleware layer in `friday-os` that intercepts every Agent Action *before* execution.

#### A. Mechanical Detection (The Reflex)
*   **Identical Tool Counter:** Buffer last 5 calls. If `Tool(A, args)` appears 3 times consecutively -> **INTERRUPT**.
*   **Oscillation Detection:** Detect A -> B -> A -> B patterns.

#### B. Cognitive Detection (The Introspection)
*   **Error Spin Protection:** Count consecutive outputs containing "Error". After 3 spins, force "Reflect".

### 4.2 The Event Bus (The Spine)
*   **Producers:** Task Agents, Monitors, Janitors, **Safety Kernel**.
*   **Consumers:** The Sentinel, The OS Kernel.
*   **Events:** `TaskCompleted`, `SystemAlert` (Low Memory), `AgentStuck` (Loop Detected), `HumanInterventionRequired`.

### 4.3 `packages/friday-tools` (The Capability Layer)
Logic currently trapped in `memory-chat.py` moves here.
*   `MemoryInspectionTool` / `MemoryMaintenanceTool`.
*   `SystemHealthTool`.
*   `WebMonitorTool`.

### 4.4 `packages/friday-agent` (The Actor Layer)
1.  **`InteractiveAgent`:** User-driven, stateless.
2.  **`AutonomousAgent`:** Goal-driven, stateful, capable of `pause()` for HITL.
3.  **`SentinelAgent`:** Event-driven, low-latency, read-only access.

## 5. Build Plan & Ordering (Bottom-Up)

### Phase 1: Tool Liberation
*   **Goal:** Enable agents to act.
*   **Tasks:** Extract `memory-chat.py` logic into `friday-tools`. Build `MemoryMaintenanceTool`.

### Phase 2: Agent Foundations
*   **Goal:** Define the actors.
*   **Tasks:** Define `InteractiveAgent` vs `AutonomousAgent` in `friday-agent`. Implement `AgentBase` loop protection.

### Phase 3: The Friday OS
*   **Goal:** Build the runtime.
*   **Tasks:**
    *   Create `packages/friday-os`.
    *   Implement `EventBus`, `Scheduler` (Day/Night toggling).
    *   Implement **`SafetyKernel`** middleware.
    *   Implement **Sentinel Layer** (Parallel Supervisor).

### Phase 4: The Application (`apps/friday-cli`)
*   **Goal:** The User Interface.
*   **Tasks:**
    *   `friday run`: The TUI that renders Chat + Status Line.
    *   `friday doctor`: Wraps `MemoryInspectionTool`.

## 6. Technical Stack
*   **Language:** Python 3.10+
*   **Concurrency:** `asyncio`
*   **DB:** SQLite (WAL Mode), ChromaDB, ElementX.
*   **CLI:** Typer
*   **TUI:** Textual

## 7. Open Questions
*   **Watchdog:** Who watches the watcher? If Sentinel crashes, do we need a systemd/supervisord wrapper? (V2 scope).
