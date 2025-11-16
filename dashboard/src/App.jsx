import { useEffect, useMemo, useState } from "react";
import Section from "./components/Section.jsx";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_URL = API_BASE.replace("http", "ws") + "/ws/events";

const useCollection = (endpoint) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/${endpoint}`);
        if (!res.ok) throw new Error("Failed to fetch " + endpoint);
        const payload = await res.json();
        if (mounted) setData(payload);
      } catch (err) {
        console.error(err);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [endpoint]);

  return { data, loading };
};

export default function App() {
  const anomalies = useCollection("anomalies");
  const classes = useCollection("classifications");
  const predictions = useCollection("predictions");
  const alerts = useCollection("alerts");
  const fl = useCollection("fl-events");
  const [liveEvents, setLiveEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setLiveEvents((prev) => [payload, ...prev].slice(0, 20));
    };
    ws.onerror = (err) => console.error("ws error", err);
    return () => ws.close();
  }, []);

  const flSummary = useMemo(() => {
    if (!fl.data.length) return null;
    const latest = fl.data[0];
    return {
      round: latest.round_id,
      accuracy: latest.accuracy,
      f1: latest.f1_score,
      epsilon: latest.epsilon,
    };
  }, [fl.data]);

  return (
    <div className="layout">
      <header className="page-header">
        <h1>Federated Network Attack Detection</h1>
        <p>Kafka powered situational awareness across anomalies, classifiers, and FL health.</p>
      </header>

      <div className="grid">
        <Section title="Anomalies">
          {anomalies.loading ? (
            <p>Loading...</p>
          ) : (
            <ul className="list">
              {anomalies.data.map((a) => (
                <li key={`${a.flow_id}-${a.created_at}`}>
                  <strong>{a.detector}</strong> score {a.score.toFixed(2)} –{" "}
                  {a.is_anomaly ? "Anomaly" : "Normal"}
                </li>
              ))}
            </ul>
          )}
        </Section>

        <Section title="Threat Classifier">
          {classes.loading ? (
            <p>Loading...</p>
          ) : (
            <ul className="list">
              {classes.data.map((c) => (
                <li key={`${c.flow_id}-${c.created_at}`}>
                  <strong>{c.label.toUpperCase()}</strong> – votes from {c.supporting_detectors.join(", ")}
                </li>
              ))}
            </ul>
          )}
        </Section>

        <Section title="GNN Predictor">
          {predictions.loading ? (
            <p>Loading...</p>
          ) : (
            <ul className="list">
              {predictions.data.map((p) => (
                <li key={`${p.flow_id}-${p.created_at}`}>
                  Severity {(p.severity * 100).toFixed(0)}% – {p.explanation}
                </li>
              ))}
            </ul>
          )}
        </Section>

        <Section title="Alerts">
          {alerts.loading ? (
            <p>Loading...</p>
          ) : (
            <ul className="list">
              {alerts.data.map((a) => (
                <li key={`${a.flow_id}-${a.created_at}`}>
                  [{a.severity}] {a.title}
                </li>
              ))}
            </ul>
          )}
        </Section>

        <Section title="FL Health">
          {flSummary ? (
            <div className="stats">
              <div>
                <span>Round</span>
                <strong>{flSummary.round}</strong>
              </div>
              <div>
                <span>Accuracy</span>
                <strong>{(flSummary.accuracy * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span>F1 Score</span>
                <strong>{(flSummary.f1 * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span>Epsilon</span>
                <strong>{flSummary.epsilon?.toFixed(2) ?? "–"}</strong>
              </div>
            </div>
          ) : (
            <p>No FL metrics yet.</p>
          )}
        </Section>

        <Section title="Live Event Stream">
          <ul className="list">
            {liveEvents.map((event, idx) => (
              <li key={idx}>
                <strong>{event.type}</strong> – {JSON.stringify(event.payload).slice(0, 120)}
              </li>
            ))}
          </ul>
        </Section>
      </div>
    </div>
  );
}
