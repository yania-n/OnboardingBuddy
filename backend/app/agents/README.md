# Specialist Agents Module

This module contains the LLM-powered specialized agents that drive the OnboardingBuddy platform. They are built using the **Google GenAI** library to analyze files and generate structured markdown outputs.

## Agent Architecture

- **`org_expert.py`**:
  - Scans all policy files in **Google Cloud Storage (GCS)** to construct a graph representation of the company's hierarchy.
  - Generates a personalized "Org Brief" for joiners outlining where their team sits in the company.

- **`learning_expert.py`**:
  - Dynamically drafts a personalized 30-60-90 Day learning plan for a specific role.
  - Caches generated markdown files and reuses them if a similar role is onboarded.
- **`plan_generator.py`**:
  - Deterministic rule-based synthesizer engine (non-LLM) that compiles company milestones, tool matrices, SLAs, and outputs from specialist agents into structured 6-phase checklists.

- **`qa_chatbot.py`**:
  - Standard conversation agent utilizing RAG semantic queries to retrieve answers.
  - Restricts responses to company documentation and escalates to the manager when answers are missing.
