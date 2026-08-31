# OnboardingBuddy Frontend

This is the React web client for **OnboardingBuddy**, built using **Vite**, **React**, and styled with **TailwindCSS**. It provides interactive portals for both new hires (Joiners) and administrators/managers.

## Portals & Features

1. **New Joiner Portal**:
   - **Interactive Phased Roadmap**: Visual step-by-step checklist of onboarding tasks (Welcome, Bearings, Learning, Hands Dirty, etc.) with real-time progress indicators.
   - **Grounded AI Assistant**: Chat with the onboarding buddy bot to ask questions about company policy. Features full citation overlays pointing to the matching handbook file and line numbers.
   - **Personalized Learning Plan**: Direct access to a customized 30-60-90 day learning curriculum generated for their specific role.
   - **Org Brief**: High-level overview of their team, department, key contacts, and business unit.

2. **Admin & Manager Portal**:
   - **New Joiner Form**: Profiling engine to create new hires, which automatically generates a default personalized onboarding plan.
   - **Onboarding Plan Live Editor**: Preview and edit drafted plans, update description fields, delete tasks, or append custom onboarding items.
   - **Dashboard Analytics**: Visualized summary statistics on total new joiners, active plans, average task progress, and department distribution.
   - **Missing Information Feedback Center**: View and inspect queries from employees that the AI could not answer. Managers can resolve them by updating the KB or delete irrelevant logs.
   - **Learning Plan Registry**: Edit generated learning plans directly inside a Markdown text editor.

## Live Cloud Run Deployment

The production React frontend is compiled and hosted at:
👉 **[https://onboarding-buddy-517395366109.europe-southwest1.run.app](https://onboarding-buddy-517395366109.europe-southwest1.run.app)**

---

## Getting Started

### Prerequisites

- Node.js (v18+)
- npm or yarn

### Local Development

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   The application will be running on `http://127.0.0.1:5173` with automated API proxying to `http://127.0.0.1:8000`.

### Production Build

To build the static assets for production deployment:
```bash
npm run build
```
This bundles the optimized application into `frontend/dist/`, which is directly served by FastAPI on Cloud Run.

