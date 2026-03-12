# E-Voting System Refactoring Report

**Course:** BSCS 3, 2 - Software Construction  
**Institution:** Uganda Christian University  
**Date:** March 2026

## Project Overview
This project involved refactoring a monolithic, single-file e-voting console application into a modular, object-oriented system. The original code violated several architectural principles, including Separation of Concerns and High Cohesion. The refactored version adheres to a three-layer architecture while preserving 100% of the original feature set and user experience.

## Architectural Design

The system is organized into four distinct layers/packages:

1.  **Presentation Layer (`ui/`)**: 
    *   Handles all terminal I/O, coloring, and menu navigation.
    *   `console.py` provides reusable formatting components.
    *   `admin_ui.py`, `voter_ui.py`, and `login_ui.py` manage specific user flows.
2.  **Business Logic Layer (`services/`)**: 
    *   Contains pure Python logic for CRUD operations, eligibility checks, and vote tallying.
    *   Services are stateless and depend on a `DataStore` object (Dependency Injection).
    *   Example: `CandidateService` handles age validation and criminal record checks.
3.  **Data Layer (`data/`)**: 
    *   `DataStore`: A centralized registry replacing all global variables.
    *   `persistence.py`: Manages JSON serialization/deserialization.
4.  **Domain Models (`models/`)**: 
    *   Encapsulated classes representing system entities (e.g., `Voter`, `Candidate`, `Poll`).
    *   Models include logic for self-serialization (`to_dict`/`from_dict`).

## Principles Applied

### 1. Modular Design & Separation of Concerns
The monolith was split into 22 files. UI code never touches the JSON file, and business logic services never use `print()` or `input()`. This makes the code easier to test and maintain.

### 2. Object-Oriented Design (OOD)
Every entity is a class. We use **Composition Over Inheritance**—for example, a `Poll` object "has a" list of `Position` references. Encapsulation ensures that data like passwords are only checked via dedicated methods.

### 3. Clean Code & DRY
*   **Magic Numbers**: Extracted to `config.py`.
*   **Naming**: Used searchable, pronounceable names (e.g., `CandidateService.calculate_age` instead of `age_calc`).
*   **Helper Functions**: Repeated UI patterns (headers, tables) are centralized in `console.py`.

### 4. SOLID Principles
*   **SRP**: Each service has a single responsibility (e.g., `AuthService` only handles credentials).
*   **DIP**: High-level UI modules depend on Service abstractions, which in turn depend on the `DataStore` instance injected at runtime.

## File Structure
```text
evoting/
├── main.py              # Application entry point
├── config.py            # Configuration & constants
├── data/                # Data storage & persistence
├── models/              # Domain classes
├── services/            # Business logic
└── ui/                  # Presentation layer
```

## How to Run
```bash
python3 main.py
```
Default Admin: `admin` / `admin123`
