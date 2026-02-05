# qupid.cloud - dating made quantum 💘

Qupid is a full-stack app that runs a quantum-inspired relationship simulation. The Flask backend exposes simulation endpoints and serves a built React (Vite) frontend with a liquid-glass visual treatment.

<img width="1147" height="590" alt="landing_page" src="https://github.com/user-attachments/assets/00f62f66-bc64-47c8-9551-60bce5651b22" />

<img width="1051" height="698" alt="qupid_text_analysis" src="https://github.com/user-attachments/assets/c51ee24a-ee7a-40a9-93ee-3cfca73e2cee" />

<img width="1012" height="745" alt="qupid_analysis" src="https://github.com/user-attachments/assets/5fd1d574-8f41-489a-9da9-25def3d49d33" />


## Quantum Backend Features
- Time-dependent, two-qubit Hamiltonian with a periodic drive (Floquet form) to model evolving dynamics.
- Empathy/compatibility couplings map to interaction terms in the Hamiltonian.
- Dissipation and noise channels modeled as Lindblad operators:
  - Bit-flip, dephasing, and decay for each partner.
  - Anti-correlated dephasing and collective decay for shared dynamics.
- Floquet-Markov solver (`fmmesolve`) to evolve the system across multiple drive periods.
- “Happiness” trajectories computed from expectation values of `sz` for each partner.
- Hybrid health score combining:
  - Final-state purity and fidelity vs. an “ideal” |00> state.
  - Trajectory statistics (trend, correlation, stability, average happiness).
- Report text (“horoscope”) generated from correlation, trend, and volatility signals.
- Optional plot rendering of the two trajectories returned as base64 PNG.

## Liquid-Glass Frontend Features
- Layered holographic background with a photographic gradient plus radial light blooms.
- “Neo-glass” panels using translucency, gradient fills, and heavy `backdrop-blur` for depth.
- Multiple inner/outer shadow stacks to create refracted edges and inset glow.
- Neon accents for primary actions and state badges (cyan/pink energy cues).
- Monospace readout for numeric purity score and analysis text to emphasize diagnostics.

## Repo Layout
- `qupid/backend`: Flask API + simulation wiring
- `qupid/qupid-app`: React + Vite frontend
- `qupid/qupid_time_dependent_floquet.py`: core simulation
- `qupid/run_script.sh`: end-to-end setup and launch script

## Quick Start
From the repo root:

```bash
./qupid/run_script.sh
```

This will:
- create a Python virtual environment
- install backend requirements
- install frontend dependencies and build the UI
- start the Flask server on `http://localhost:5000`

## Manual Setup
Backend:

```bash
cd qupid
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r backend/requirements.txt
python3 backend/app.py
```

Frontend:

```bash
cd qupid/qupid-app
npm install
npm run build
```

The Flask app serves the built frontend from `qupid/qupid-app/dist`.

## API Endpoints
- `POST /run`: run a simulation with JSON parameters
- `POST /analyze-run`: upload a message file and run analysis + simulation

## Notes
- The backend uses Flask + Flask-CORS.
- The frontend is a Vite React app.
