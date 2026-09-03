# Product Requirement Document: Friday OS (V1)

## 1. Executive Summary

**Friday** has evolved from a framework into a persistent, autonomous **AI Operating System**.

This PRD defines the architecture for **`packages/friday-os`**, the infrastructure package that acts as the runtime environment. It provides the **Substrate** (Scheduler, Event Bus, Concurrency Control) and the **Safety Kernel** (Loop Detection, Resource Quotas) upon which the **Friday Application** (`apps/friday-cli`) runs.

The architecture separates the **Infrastructure** (process management, safety, memory integrity) from the **Application Logic** (personalities, specific prompts, user interaction).

## 2. Naming & Package Structure

### 2.1 `packages/friday-os` (The Infrastructure)
*   **Role:** The Kernel / Runtime.
*   **Responsibility:** Manages the "Tri-State" lifecycle (Day/Night/Sentinel), enforces safety policies (Loop Detection), manages database locks, and routes events.
*   **Analogy:** This is "Linux". It manages resources and safety so agents can run.

### 2.2 `apps/friday-cli` (The Application)
*   **Command:** `friday`
*   **Role:** The User Experience.
*   **Responsibility:** Instantiates the OS, configures the specific Agents (Chat, Janitor), connects the TUI (Textual/Rich), and handles user input.
*   **Analogy:** This is the "Desktop Environment" or "Shell".

## 3. Core Vision: The Tri-State Architecture

The OS manages three distinct operational states, each with unique **Safety Profiles**:

### 3.1 Day Mode (Active/Interactive)
*   **Trigger:** User Input.
*   **Primary Agent:** **Chat Agent** (`InteractiveAgent`).
*   **Behavior:** Serves user requests. Queues maintenance tasks.
*   **Safety Profile:** **Lenient**.
    *   *Looping:* Warn user, allow override.
    *   *Errors:* Show stack trace to user, ask for guidance.

### 3.2 Night Mode (Sleep/Dream)
*   **Trigger:** `/sleep` command or Inactivity Timeout.
*   **Primary Agent:** **Janitor Agent** (`AutonomousAgent`).
*   **Behavior:** Consolidation, Refactoring, Deep Work.
*   **Safety Profile:** **Strict**.
    *   *Looping:* **Hard Stop**. Suspend agent. Emit `AgentStuck` event.
    *   *Errors:* Max 2 retries. On failure, rollback transaction and log to Morning Report.

### 3.3 Sentinel Mode (The Nervous System)
*   **Trigger:** Always On (Sidecar / Background Threads).
*   **Primary Agent:** **Sentinel Agent** (Supervisor).
*   **Behavior:** Monitor External/Internal events. Dispatch `Alerts`.
*   **Safety Profile:** **Mission Critical**.
    *   *Looping:* Restart process immediately (Watchdog).
    *   *Errors:* Fallback to primitive logging. Must never crash the OS.

## 4. System Architecture

### 4.1 The Safety Kernel (The Immune System)
A middleware layer in `friday-os` that intercepts every Agent Action *before* execution.

#### A. Mechanical Detection (The Reflex)
*   **Identical Tool Counter:**
    *   *Logic:* Buffer last 5 calls. If `Tool(A, args)` appears 3 times consecutively -> **INTERRUPT**.
    *   *Action:* Inject System Message: *"Error: Recursive tool call detected. Stop and change strategy."*
*   **Oscillation Detection:**
    *   *Logic:* Detect A -> B -> A -> B patterns.
    *   *Action:* Force a "Reflect" step.

#### B. Cognitive Detection (The Introspection)
*   **Error Spin Protection:**
    *   *Logic:* Count consecutive outputs containing "Error" or "Exception".
    *   *Action:* After 3 spins, inject: *"You are stuck in an error loop. Analyze WHY before retrying."*
*   **Semantic Similarity (Advanced):**
    *   *Logic:* If embedding of Action(N) is >0.95 similar to Action(N-1) despite different phrasing.

### 4.2 The Event Bus (The Spine)
*   **Producers:** Task Agents, Monitors, Janitors, **Safety Kernel**.
*   **Consumers:** The Sentinel, The OS Kernel.
*   **Events:** `TaskCompleted`, `SystemAlert` (Low Memory), `AgentStuck` (Loop Detected), `HumanInterventionRequired`.

### 4.3 Concurrency & Data Integrity
*   **Shared Database / WAL:** SQLite for Transcript/Episodic memory.
*   **Optimistic Locking:** For Graph/Vector stores.
*   **Interrupts:** Sentinel alerts have kernel-level priority to inject messages into the stdout stream.

### 4.4 `packages/friday-tools` (The Capability Layer)
Logic currently trapped in `memory-chat.py` moves here.
*   `MemoryInspectionTool` / `MemoryMaintenanceTool`.
*   `SystemHealthTool`.
*   `WebMonitorTool`.

### 4.5 `packages/friday-agent` (The Actor Layer)
1.  **`InteractiveAgent`:** User-driven, stateless.
2.  **`AutonomousAgent`:** Goal-driven, stateful, capable of `pause()` for HITL.
3.  **`SentinelAgent`:** Event-driven, low-latency.

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
    *   Implement `EventBus`, `Scheduler`.
    *   Implement **`SafetyKernel`** middleware.

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
