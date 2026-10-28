# WindLens — Wind Generation Intelligence

WindLens is a wind generation forecasting analysis dashboard designed to help UK energy procurement teams understand the accuracy of day-ahead wind forecasts. It compares published wind generation forecasts with actual delivered generation to quantify forecast errors and support better-informed procurement decisions.

## Live Application

- **Frontend:** https://windlens-nine.vercel.app/
- **Backend API:** https://windlens-api-ncr6.onrender.com
- **API Health Check:** https://windlens-api-ncr6.onrender.com/health
- **Monthly Analysis API:** https://windlens-api-ncr6.onrender.com/api/monthly-analysis
- **GitHub Repository:** https://github.com/Harshil0309/windlens

## Features

- **Monthly performance overview:** Analyze wind forecast accuracy across January 2026.
- **Daily forecast analysis:** Select a delivery date and compare forecast wind generation against actual generation.
- **Forecast error metrics:** Calculate Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), forecast bias, and Weighted Absolute Percentage Error (WAPE).
- **Forecast vintage selection:** Select the latest available forecast published before the configured day-ahead cutoff.
- **Interactive dashboard:** Explore daily forecast performance and monthly analysis through a React-based interface.
- **Containerized deployment:** Run the frontend and backend locally using Docker Compose.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Data processing | Pandas, NumPy |
| HTTP requests | HTTPX |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |
| Frontend deployment | Vercel |
| Backend deployment | Render |
| Data source | Elexon Insights API |

## Architecture

```text
                  ┌────────────────────────┐
                  │      React + Vite      │
                  │   WindLens Dashboard   │
                  └────────────┬───────────┘
                               │
                         HTTP GET requests
                               │
                  ┌────────────▼───────────┐
                  │      FastAPI Backend   │
                  │                        │
                  │  Data Retrieval        │
                  │  Forecast Selection    │
                  │  Error Calculations    │
                  └────────────┬───────────┘
                               │
                         Elexon API
                               │
                  ┌────────────▼───────────┐
                  │ Actual Wind Generation │
                  │ Published Forecasts    │
                  └────────────────────────┘
```

The frontend requests analysis from the FastAPI backend. The backend retrieves the relevant Elexon data, processes forecast and actual generation records, calculates performance metrics, and returns JSON responses to the dashboard.

## Data Source

WindLens uses the [Elexon Insights API](https://data.elexon.co.uk/swagger/v1/swagger.json) to retrieve electricity market data.

The analysis covers **1 January 2026 through 31 January 2026**.

The relevant data endpoints are:

- `FUELHH/stream` — half-hourly actual generation data, filtered to wind.
- `WINDFOR/stream` — published wind generation forecasts.

Actual generation is recorded at half-hourly intervals, while forecast data is hourly. The analysis aligns the data at an hourly level by aggregating the corresponding half-hourly actual values using their mean.

## Forecast Selection Methodology

For each delivery day, WindLens uses a configured day-ahead forecast publication cutoff of **11:00 UTC on the previous day**.

The selection process is:

1. Identify the forecast records associated with the delivery date.
2. Filter forecast vintages to those published on or before the configured cutoff.
3. Select the latest eligible forecast vintage.
4. Align hourly forecast values with hourly actual generation values.
5. Calculate forecast accuracy metrics from the aligned observations.

The 11:00 UTC cutoff is a **project assumption** and should be validated against the intended procurement decision timeline and the applicable market publication rules before operational use.

## Forecast Accuracy Metrics

Let \(F_t\) denote forecast generation and \(A_t\) denote actual generation for observation \(t\), with \(n\) aligned observations.

### Mean Absolute Error (MAE)

Measures the average magnitude of forecast errors.

\[
MAE=\frac{1}{n}\sum_{t=1}^{n}|F_t-A_t|
\]

Lower values indicate smaller average absolute errors.

### Root Mean Squared Error (RMSE)

Penalizes larger errors more heavily by squaring each error before averaging.

\[
RMSE=\sqrt{\frac{1}{n}\sum_{t=1}^{n}(F_t-A_t)^2}
\]

Lower values indicate better forecast accuracy.

### Forecast Bias

Measures the average signed difference between forecast and actual generation.

\[
Bias=\frac{1}{n}\sum_{t=1}^{n}(F_t-A_t)
\]

- Positive bias indicates that forecasts are higher than actual generation on average.
- Negative bias indicates that forecasts are lower than actual generation on average.

### Weighted Absolute Percentage Error (WAPE)

Expresses the sum of absolute forecast errors relative to total actual generation.

\[
WAPE=\frac{\sum_{t=1}^{n}|F_t-A_t|}{\sum_{t=1}^{n}|A_t|}\times100
\]

Lower values indicate smaller absolute errors relative to actual generation. The implementation should explicitly handle cases where the denominator is zero.

## Prerequisites

Choose either the local development setup or the Docker setup.

### Option 1: Local Development

Install:

- Python 3.12 or a compatible version supported by the project dependencies.
- Node.js and npm.
- Git.

### Option 2: Docker

Install Docker Desktop with Docker Compose support.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Harshil0309/windlens.git
cd windlens
```

### 2. Start the backend

Open a terminal in the project root.

On Windows:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

If PowerShell blocks virtual environment activation, you can run the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The backend will be available at:

- API base: http://localhost:8000
- Health check: http://localhost:8000/health
- Interactive API documentation: http://localhost:8000/docs

### 3. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Create a `.env` file inside the `frontend/` directory with the following content:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the Vite development server:

```powershell
npm run dev
```

Open http://localhost:5173 in your browser.

The frontend's API base URL must point to the backend that serves the analysis endpoints.

## Run with Docker Compose

From the project root, run:

```bash
docker compose up --build
```

Docker Compose builds and starts the frontend and backend containers.

Open the application at:

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/health
- Backend API documentation: http://localhost:8000/docs

To stop the containers:

```bash
docker compose down
```

To rebuild the application after making code changes:

```bash
docker compose up --build
```

The frontend Docker image receives `VITE_API_BASE_URL` as a build argument. The configured URL must be reachable by the user's browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks backend health. |
| GET | `/api/monthly-analysis` | Returns monthly forecast analysis and performance metrics. |
| GET | `/api/forecast?delivery_date=2026-01-28` | Returns forecast analysis for a selected delivery date. |

Example health check:

```bash
curl http://localhost:8000/health
```

Example daily analysis request:

```bash
curl "http://localhost:8000/api/forecast?delivery_date=2026-01-28"
```

Example monthly analysis request:

```bash
curl http://localhost:8000/api/monthly-analysis
```

## Running Tests

From the backend directory, with its virtual environment activated:

```bash
python -m pytest -v
```

The test suite covers backend functionality. Run the tests before submitting changes or deploying an updated version.

## Deployment

### Frontend — Vercel

The frontend is deployed on Vercel.

Configure the following project settings:

- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variable:

```env
VITE_API_BASE_URL=https://windlens-api-ncr6.onrender.com
```

Redeploy after changing environment variables. Since Vite embeds environment variables during the build, a new frontend build is required for changes to take effect.

### Backend — Render

The FastAPI backend is deployed on Render.

Configure the backend service to build using `backend/Dockerfile` or the equivalent Python build and start commands supported by the service configuration.

The Dockerfile-based deployment uses the command configured in `backend/Dockerfile`.

Ensure the backend CORS configuration allows requests from the deployed frontend origin:

```text
https://windlens-nine.vercel.app
```

Do not include a trailing slash in the configured origin.

## Project Structure

```text
windlens/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── api/
│   │       └── routes.py
│   ├── tests/
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml
├── .gitignore
└── README.md
```

The tree above highlights the main project files; individual components and additional files may exist in the repository.

## Assumptions and Limitations

- The analysis period is January 2026.
- The day-ahead forecast cutoff is assumed to be 11:00 UTC on the preceding day.
- Half-hourly actual generation is aggregated to an hourly mean to align it with hourly forecast data.
- Forecast accuracy metrics depend on the availability, timestamps, units, and correct alignment of source records.
- A forecast publication cutoff is a modeling assumption, not a guarantee that a forecast was available to every procurement participant at that time.
- Forecast errors alone do not establish the financial impact of a procurement decision. A commercial assessment would also require relevant market prices, settlement rules, and procurement assumptions.
- This application is an analytical prototype and should not be treated as an operational trading or procurement recommendation without further validation.

## Future Improvements

Potential extensions include forecast vintage comparisons, additional historical periods, procurement-oriented cost analysis, and more detailed data-quality monitoring.

## License

No license has been specified. Unless a license is added to the repository, reuse and redistribution are subject to the applicable default copyright rules.
