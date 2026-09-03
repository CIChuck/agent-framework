# Product Requirement Document: Friday OS & Platform Architecture (V4)

## 1. Executive Summary

**Friday** is a persistent, autonomous **AI System**.

This PRD defines the architecture for **`packages/friday-os`**, the infrastructure package that acts as the operating system for the agentic ecosystem. It provides the runtime environment (Scheduler, Event Bus, Concurrency Control) upon which the **Friday Application** (`apps/friday-cli`) runs.

The architecture separates the **Infrastructure** (process management, safety, memory integrity) from the **Application Logic** (personalities, specific prompts, user interaction).

## 2. Naming & Package Structure

### 2.1 `packages/friday-os` (The Infrastructure)
*   **Role:** The Kernel / Runtime.
*   **Responsibility:** Manages the "Tri-State" lifecycle (Day/Night/Sentinel), enforces safety policies, manages database locks, and routes events.
*   **Analogy:** This is "Linux" or "Windows". It doesn't chat with you; it enables the things that do.

### 2.2 `apps/friday-cli` (The Application)
*   **Command:** `friday`
*   **Role:** The User Experience.
*   **Responsibility:** Instantiates the OS, configures the specific Agents (Chat, Janitor), connects the TUI (Textual/Rich), and handles user input.
*   **Analogy:** This is the "Desktop Environment" or "Shell".

## 3. Core Vision: The Tri-State Architecture

The OS manages three distinct operational states:

### 3.1 Day Mode (Active/Interactive)
*   **Trigger:** User Input.
*   **Primary Agent:** **Chat Agent** (`InteractiveAgent`).
*   **OS Responsibility:** Prioritize latency. Hold Write Lock on Episodic Buffer; Read Lock on Graph/Vector stores. Route user `stdin` to Agent.

### 3.2 Night Mode (Sleep/Dream)
*   **Trigger:** `/sleep` command or Inactivity Timeout.
*   **Primary Agent:** **Janitor Agent** (`AutonomousAgent`).
*   **OS Responsibility:** Prioritize throughput. Upgrade to Write Lock on Graph/Vector stores. Schedule resource-intensive jobs.

### 3.3 Sentinel Mode (The Nervous System)
*   **Trigger:** Always On (Sidecar / Background Threads).
*   **Primary Agent:** **Sentinel Agent** (Supervisor).
*   **OS Responsibility:** Run the **Event Bus**. Dispatch `Alert` events. Monitor system health (RAM/CPU). Inject interrupts into the Day/Night streams.

## 4. System Architecture

### 4.1 The Event Bus (The Spine)
Implemented in `friday-os`, this is the central nervous system.
*   **Producers:** Task Agents, Monitors, Janitors.
*   **Consumers:** The Sentinel, The OS Kernel.
*   **Events:** `TaskCompleted`, `SystemAlert` (Low Memory), `ExternalTrigger` (Stock Drop), `HumanInterventionRequired`.

### 4.2 Concurrency & Data Integrity
The OS enforces "Single Source of Truth" via DB Locking strategies:
*   **Shared Database / WAL:** SQLite for Transcript/Episodic memory allows concurrent reads (Inspect) and writes (Chat).
*   **Optimistic Locking:** For Graph/Vector stores managed by the OS.
*   **Interrupts:** Sentinel alerts have kernel-level priority to inject messages into the stdout stream.

### 4.3 `packages/friday-tools` (The Capability Layer)
Logic currently trapped in `memory-chat.py` moves here.
*   `MemoryInspectionTool` / `MemoryMaintenanceTool`.
*   `SystemHealthTool`.
*   `WebMonitorTool`.

### 4.4 `packages/friday-agent` (The Actor Layer)
1.  **`InteractiveAgent`:** User-driven, stateless.
2.  **`AutonomousAgent`:** Goal-driven, stateful, capable of `pause()` for HITL.
3.  **`SentinelAgent`:** Event-driven, low-latency.

## 5. Build Plan & Ordering (Bottom-Up)

### Phase 1: Tool Liberation
*   **Goal:** Enable agents to act.
*   **Tasks:** Extract `memory-chat.py` logic into `friday-tools`. Build `MemoryMaintenanceTool` and `SystemHealthTool`.

### Phase 2: Agent Foundations
*   **Goal:** Define the actors.
*   **Tasks:** Define `InteractiveAgent` vs `AutonomousAgent` vs `SentinelAgent` in `friday-agent`.

### Phase 3: The Friday OS
*   **Goal:** Build the runtime.
*   **Tasks:**
    *   Create `packages/friday-os`.
    *   Implement `EventBus`, `Scheduler`, and `WorldState`.
    *   Implement `SafetyKernel` (Policy Enforcer).

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
*   **Notifications:** How does Sentinel notify if the `friday` app is closed? (Future: System Tray integration or Email).
