
import { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  CalendarDays,
  CheckCircle2,
  Clock3,
  RefreshCw,
  Wind,
  Zap,
} from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface ComparisonPoint {
  start_time: string;
  actual_mw: number;
  forecast_mw: number;
  error_mw: number;
}

interface AnalysisResponse {
  delivery_date: string;
  decision_time: string;
  forecast_interval_count: number;
  actual_interval_count: number;
  comparison_interval_count: number;
  metrics: {
    sample_count: number;
    mae_mw: number | null;
    rmse_mw: number | null;
    bias_mw: number | null;
    wape_percent: number | null;
  };
  comparison: ComparisonPoint[];
}


interface DailyResult {
  delivery_date: string;
  sample_count: number;
  mae_mw: number | null;
  bias_mw: number | null;
  wape_percent: number | null;
}

interface MonthlyResponse {
  month: string;
  decision_cutoff_rule: string;
  metrics: {
    sample_count: number;
    mae_mw: number | null;
    rmse_mw: number | null;
    bias_mw: number | null;
    wape_percent: number | null;
  };
  days_with_comparisons: number;
  daily_results: DailyResult[];
}


function formatMW(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return "—";
  return `${(value / 1000).toFixed(2)} GW`;
}

function formatNumber(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return "—";
  return value.toLocaleString("en-GB", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  });
}

function formatHour(value: string) {
  return new Date(value).toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    hour12: false,
  });
}

function App() {
  const [deliveryDate, setDeliveryDate] = useState("2026-01-01");
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
const [monthlyData, setMonthlyData] = useState<MonthlyResponse | null>(null);
const [monthlyLoading, setMonthlyLoading] = useState(true);
const [monthlyError, setMonthlyError] = useState("");

useEffect(() => {
  let cancelled = false;

  async function loadMonthlyAnalysis() {
    setMonthlyLoading(true);
    setMonthlyError("");

    try {
      const response = await fetch(`${API_URL}/api/monthly-analysis`);

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(
          body?.detail || `Monthly request failed: ${response.status}`,
        );
      }

      const result: MonthlyResponse = await response.json();

      if (!cancelled) {
        setMonthlyData(result);
      }
    } catch (err) {
      if (!cancelled) {
        setMonthlyError(
          err instanceof Error ? err.message : "Unable to load monthly analysis.",
        );
      }
    } finally {
      if (!cancelled) {
        setMonthlyLoading(false);
      }
    }
  }

  void loadMonthlyAnalysis();

  return () => {
    cancelled = true;
  };
}, []);

  

  async function loadAnalysis(date: string) {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/forecast?delivery_date=${date}`,
      );

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(
          body?.detail || `Request failed with status ${response.status}`,
        );
      }

      const result: AnalysisResponse = await response.json();
      setData(result);
    } catch (err) {
      setData(null);
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load wind analysis.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAnalysis(deliveryDate);
  }, [deliveryDate]);

  const metrics = data?.metrics;
  const bias = metrics?.bias_mw ?? null;
  const isOverforecast = bias !== null && bias > 0;
  const isUnderforecast = bias !== null && bias < 0;
  
  const worstDays = [...(monthlyData?.daily_results ?? [])]
    .sort((a, b) => (b.mae_mw ?? -1) - (a.mae_mw ?? -1))
    .slice(0, 5);


  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" aria-label="WindLens home">
          <span className="brand-mark">
            <Wind size={23} strokeWidth={2.2} />
          </span>
          <span>
            <span className="brand-name">windlens</span>
            <span className="brand-subtitle">ENERGY INTELLIGENCE</span>
          </span>
        </a>

        <div className="sidebar-section-label">WORKSPACE</div>
        <div className="nav-item active">
          <Activity size={18} />
          <span>Wind analysis</span>
        </div>
        <div className="nav-item muted">
          <Zap size={18} />
          <span>Procurement insights</span>
          <span className="coming-soon">SOON</span>
        </div>

        <div className="sidebar-bottom">
          <div className="status-indicator">
            <span className="status-dot" />
            <span>Analysis workspace</span>
          </div>
          <p>UK electricity market</p>
          <p className="sidebar-footnote">Data source: Elexon BMRS</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> Wind analysis
          </div>
          <div className="topbar-right">
            <span className="live-dot" />
            <span>Historical analysis</span>
            <div className="avatar">WL</div>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                RENEWABLES · PROCUREMENT
              </div>
              <h1>Wind generation intelligence</h1>
              <p className="page-description">
                Compare published wind forecasts with delivered generation
                to understand forecast error before procurement decisions.
              </p>
            </div>

            <div className="date-control">
              <label htmlFor="delivery-date">
                <CalendarDays size={16} />
                DELIVERY DATE
              </label>
              <select
                id="delivery-date"
                value={deliveryDate}
                onChange={(event) => setDeliveryDate(event.target.value)}
              >
                {Array.from({ length: 31 }, (_, index) => {
                  const day = String(index + 1).padStart(2, "0");
                  const value = `2026-01-${day}`;
                  return (
                    <option key={value} value={value}>
                      {new Date(`${value}T12:00:00Z`).toLocaleDateString(
                        "en-GB",
                        {
                          day: "2-digit",
                          month: "long",
                          year: "numeric",
                          timeZone: "UTC",
                        },
                      )}
                    </option>
                  );
                })}
              </select>
            </div>
          </section>

          {error && (
            <div className="error-banner" role="alert">
              <AlertCircle size={20} />
              <div>
                <strong>Unable to load analysis</strong>
                <p>{error}</p>
                <p>
                  Check that the FastAPI backend is running at{" "}
                  <code>{API_URL}</code>.
                </p>
              </div>
              <button
                className="retry-button"
                onClick={() => void loadAnalysis(deliveryDate)}
              >
                <RefreshCw size={15} /> Retry
              </button>
            </div>
          )}

          <section className="overview-row">
            <div className="section-heading">
              <div>
                <h2>Performance overview</h2>
                <p>Forecast accuracy for the selected delivery day</p>
              </div>
              <span className="period-tag">JAN 2026</span>
            </div>

            <div className="metrics-grid">
              <article className="metric-card">
                <div className="metric-top">
                  <span className="metric-label">Mean absolute error</span>
                  <span className="metric-icon blue">
                    <Activity size={18} />
                  </span>
                </div>
                <div className="metric-value">
                  {loading ? "Loading…" : formatMW(metrics?.mae_mw)}
                </div>
                <div className="metric-footer">
                  <span className="metric-context">
                    Average absolute deviation
                  </span>
                </div>
              </article>

              <article className="metric-card">
                <div className="metric-top">
                  <span className="metric-label">Weighted error</span>
                  <span className="metric-icon purple">
                    <Zap size={18} />
                  </span>
                </div>
                <div className="metric-value">
                  {loading || metrics?.wape_percent == null
                    ? loading
                      ? "Loading…"
                      : "—"
                    : `${formatNumber(metrics.wape_percent)}%`}
                </div>
                <div className="metric-footer">
                  <span className="metric-context">
                    WAPE across matched hours
                  </span>
                </div>
              </article>

              <article className="metric-card">
                <div className="metric-top">
                  <span className="metric-label">Forecast bias</span>
                  <span
                    className={`metric-icon ${
                      isOverforecast
                        ? "orange"
                        : isUnderforecast
                          ? "green"
                          : "blue"
                    }`}
                  >
                    {isUnderforecast ? (
                      <ArrowDownRight size={18} />
                    ) : (
                      <ArrowUpRight size={18} />
                    )}
                  </span>
                </div>
                <div className="metric-value">
                  {loading ? "Loading…" : formatMW(bias)}
                </div>
                <div className="metric-footer">
                  <span
                    className={`bias-indicator ${
                      isOverforecast
                        ? "bias-high"
                        : isUnderforecast
                          ? "bias-low"
                          : ""
                    }`}
                  >
                    {bias === null
                      ? "Mean forecast − actual"
                      : bias > 0
                        ? "Overforecast on average"
                        : bias < 0
                          ? "Underforecast on average"
                          : "No average bias"}
                  </span>
                </div>
              </article>

              <article className="metric-card">
                <div className="metric-top">
                  <span className="metric-label">Matched hours</span>
                  <span className="metric-icon green">
                    <CheckCircle2 size={18} />
                  </span>
                </div>
                <div className="metric-value">
                  {loading
                    ? "Loading…"
                    : `${data?.comparison_interval_count ?? 0}/24`}
                </div>
                <div className="metric-footer">
                  <span className="metric-context">
                    Complete hourly comparisons
                  </span>
                </div>
              </article>
            </div>
          </section>

          <section className="chart-card">
            <div className="chart-header">
              <div>
                <div className="chart-title-row">
                  <h2>Forecast vs actual generation</h2>
                  <span className="data-badge">
                    <span /> ELEXON DATA
                  </span>
                </div>
                <p>
                  Hourly wind generation across the selected delivery day
                </p>
              </div>
              <div className="chart-unit">UNIT: GW</div>
            </div>

            {loading ? (
              <div className="chart-state">
                <RefreshCw className="spin" size={25} />
                <p>Loading generation data…</p>
              </div>
            ) : error ? (
              <div className="chart-state">
                <AlertCircle size={25} />
                <p>Chart unavailable until the API connection is restored.</p>
              </div>
            ) : !data?.comparison.length ? (
              <div className="chart-state">
                <AlertCircle size={25} />
                <p>No matched hourly observations are available for this day.</p>
              </div>
            ) : (
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={data.comparison}
                    margin={{ top: 12, right: 14, left: 2, bottom: 4 }}
                  >
                    <CartesianGrid
                      stroke="#e9edf3"
                      strokeDasharray="4 5"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="start_time"
                      tickFormatter={formatHour}
                      tick={{ fill: "#7b8497", fontSize: 11 }}
                      axisLine={{ stroke: "#dfe4ec" }}
                      tickLine={false}
                      minTickGap={28}
                    />
                    <YAxis
                      domain={["auto", "auto"]}
                      tickFormatter={(value: number) =>
                        (value / 1000).toFixed(0)
                      }
                      tick={{ fill: "#7b8497", fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      tickMargin={9}
                      width={43}
                    />
                    <Tooltip
                      labelFormatter={(label) =>
                        `${formatHour(String(label))} UTC`
                      }
                      formatter={(value, name) => [
                        `${(Number(value) / 1000).toFixed(3)} GW`,
                        name === "forecast_mw"
                          ? "Forecast"
                          : "Actual generation",
                      ]}
                      contentStyle={{
                        borderRadius: 12,
                        border: "1px solid #e5e9f0",
                        boxShadow: "0 8px 28px rgba(20, 35, 60, 0.1)",
                        fontSize: 12,
                      }}
                    />
                    <Legend
                      verticalAlign="top"
                      align="right"
                      height={36}
                      iconType="circle"
                      iconSize={8}
                      formatter={(value) =>
                        value === "forecast_mw"
                          ? "Published forecast"
                          : "Actual generation"
                      }
                    />
                    <ReferenceLine y={0} stroke="#dfe4ec" />
                    <Line
                      type="monotone"
                      dataKey="forecast_mw"
                      name="forecast_mw"
                      stroke="#6875e8"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5, strokeWidth: 0 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="actual_mw"
                      name="actual_mw"
                      stroke="#13a887"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5, strokeWidth: 0 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            <div className="chart-footnote">
              <Clock3 size={14} />
              <span>
                All timestamps shown in UTC. Actual generation is averaged
                from two half-hour observations per hour.
              </span>
            </div>
          </section>
          
          <section className="monthly-section">
            <div className="section-heading monthly-heading">
              <div>
                <h2>January performance</h2>
                <p>Daily forecast error across the full month</p>
              </div>
              <span className="period-tag">31 DELIVERY DAYS</span>
            </div>

            {monthlyLoading ? (
              <div className="monthly-message">Loading monthly performance…</div>
            ) : monthlyError ? (
              <div className="monthly-message monthly-error">
                Monthly analysis could not load: {monthlyError}
              </div>
            ) : monthlyData ? (
              <>
                <div className="monthly-summary">
                  <div className="monthly-stat">
                    <span>Monthly MAE</span>
                    <strong>{formatMW(monthlyData.metrics.mae_mw)}</strong>
                  </div>
                  <div className="monthly-stat">
                    <span>Monthly WAPE</span>
                    <strong>
                      {monthlyData.metrics.wape_percent == null
                        ? "—"
                        : `${formatNumber(monthlyData.metrics.wape_percent)}%`}
                    </strong>
                  </div>
                  <div className="monthly-stat">
                    <span>Monthly bias</span>
                    <strong>{formatMW(monthlyData.metrics.bias_mw)}</strong>
                  </div>
                  <div className="monthly-stat">
                    <span>Matched hours</span>
                    <strong>
                      {monthlyData.metrics.sample_count.toLocaleString("en-GB")}/744
                    </strong>
                  </div>
                </div>

                <div className="monthly-chart-card">
                  <div className="monthly-card-heading">
                    <h3>Daily mean absolute error</h3>
                    <span>MW</span>
                  </div>
                  <p className="monthly-card-description">
                    Higher values indicate larger average hourly forecast deviations.
                  </p>

                  <div className="monthly-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={monthlyData.daily_results}
                        margin={{ top: 10, right: 14, left: 5, bottom: 4 }}
                      >
                        <CartesianGrid
                          stroke="#e9edf3"
                          strokeDasharray="4 5"
                          vertical={false}
                        />
                        <XAxis
                          dataKey="delivery_date"
                          tickFormatter={(value: string) => value.slice(8)}
                          tick={{ fill: "#7b8497", fontSize: 10 }}
                          axisLine={{ stroke: "#dfe4ec" }}
                          tickLine={false}
                          interval={2}
                        />
                        <YAxis
                          tickFormatter={(value: number) =>
                            (value / 1000).toFixed(1)
                          }
                          tick={{ fill: "#7b8497", fontSize: 10 }}
                          axisLine={false}
                          tickLine={false}
                          width={43}
                        />
                        <Tooltip
                          labelFormatter={(value) => `Delivery date: ${String(value)}`}
                          formatter={(value) => [
                            value == null ? "—" : `${formatNumber(Number(value))} MW`,
                            "Daily MAE",
                          ]}
                          contentStyle={{
                            borderRadius: 10,
                            border: "1px solid #e5e9f0",
                            fontSize: 12,
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="mae_mw"
                          name="Daily MAE"
                          stroke="#6977e8"
                          strokeWidth={2.5}
                          dot={{ r: 2.5, fill: "#6977e8", strokeWidth: 0 }}
                          activeDot={{ r: 5 }}
                          connectNulls={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="monthly-chart-note">
                    <Clock3 size={13} />
                    All daily values use matched hourly observations and the provisional
                    11:00 UTC day-ahead cutoff.
                  </div>
                </div>

                <div className="worst-days-card">
                  <div className="monthly-card-heading">
                    <h3>Days requiring closer review</h3>
                    <span>TOP 5 BY MAE</span>
                  </div>
                  <p className="monthly-card-description">
                    Ranked by mean absolute error, not by financial impact.
                  </p>

                  <div className="table-scroll">
                    <table className="worst-days-table">
                      <thead>
                        <tr>
                          <th>Delivery date</th>
                          <th>MAE</th>
                          <th>Bias</th>
                          <th>WAPE</th>
                        </tr>
                      </thead>
                      <tbody>
                        {worstDays.map((day) => (
                          <tr key={day.delivery_date}>
                            <td>
                              <button
                                className="date-link"
                                onClick={() => setDeliveryDate(day.delivery_date)}
                              >
                                {new Date(
                                  `${day.delivery_date}T12:00:00Z`,
                                ).toLocaleDateString("en-GB", {
                                  day: "2-digit",
                                  month: "short",
                                  timeZone: "UTC",
                                })}
                              </button>
                            </td>
                            <td>{formatMW(day.mae_mw)}</td>
                            <td>
                              <span
                                className={
                                  (day.bias_mw ?? 0) > 0
                                    ? "table-bias-positive"
                                    : (day.bias_mw ?? 0) < 0
                                      ? "table-bias-negative"
                                      : ""
                                }
                              >
                                {formatMW(day.bias_mw)}
                              </span>
                            </td>
                            <td>
                              {day.wape_percent == null
                                ? "—"
                                : `${formatNumber(day.wape_percent)}%`}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="table-footnote">
                    Select a date to open its hourly forecast and actual generation.
                  </p>
                </div>
              </>
            ) : null}
          </section>


          <section className="insight-panel">
            <div className="insight-symbol">
              <Wind size={21} />
            </div>
            <div className="insight-copy">
              <h3>Procurement context</h3>
              <p>
                {loading
                  ? "Calculating forecast performance for the selected day…"
                  : bias !== null && bias > 0
                    ? `The forecast exceeded actual wind generation by an average of ${formatMW(bias)}. Consider this deviation when assessing balancing exposure; financial impact depends on market prices and the utility's position.`
                    : bias !== null && bias < 0
                      ? `The forecast fell below actual wind generation by an average of ${formatMW(Math.abs(bias))}. Review the deviation alongside procurement positions and market prices.`
                      : bias === 0
                        ? "Forecasts matched actual generation on average. Individual hourly deviations may still affect procurement decisions."
                        : "No bias estimate is available for this delivery day. Check that matched observations are available."}
              </p>
              <span className="provisional-note">
                Illustrative analysis · Decision cutoff is provisional
              </span>
            </div>
          </section>

          <footer className="page-footer">
            <span>WINDLENS <span className="footer-separator">/</span> ENERGY ANALYTICS</span>
            <span>Source: Elexon BMRS · January 2026</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
