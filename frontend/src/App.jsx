import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import "./App.css";

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${mins}:${secs}`;
}

function Waveform() {
  return (
    <span className="waveform" aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
      <span />
    </span>
  );
}

function ScoreGauge({ score }) {
  const pct = Math.max(0, Math.min(100, score));
  return (
    <div className="gauge" style={{ "--pct": pct }}>
      <div className="overall-rating">
        {score}
        <span>/ 100</span>
      </div>
    </div>
  );
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: "#0d1530",
        border: "1px solid #1f2c52",
        borderRadius: 8,
        padding: "8px 12px",
        fontFamily: "IBM Plex Mono, monospace",
        fontSize: 12,
        color: "#eef1fb",
      }}
    >
      <div style={{ color: "#9aa5c7", marginBottom: 4 }}>
        {formatTime(label)}
      </div>
      {payload.map((entry) => (
        <div key={entry.dataKey} style={{ color: entry.color }}>
          {entry.name}: {Number(entry.value).toFixed(2)}
        </div>
      ))}
    </div>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [lyrics, setLyrics] = useState("");
  const [graphData, setGraphData] = useState([]);
  const [peak, setPeak] = useState(null);
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState("");

  async function analyzeSong() {
    if (!file || loading) return;

    setLoading(true);
    setError("");
    setReview(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("lyrics", lyrics);

    setGraphData([]);
    setPeak(null);

    try {
      const analyzedEnergy = await fetch(
        "http://127.0.0.1:8000/analyze-energy",
        {
          method: "POST",
          body: formData,
        },
      );

      if (!analyzedEnergy.ok) {
        throw new Error("Energy analysis failed");
      }

      const energyData = await analyzedEnergy.json();

      const generatedReview = await fetch(
        "http://127.0.0.1:8000/generate-review",
        {
          method: "POST",
          body: formData,
        },
      );

      if (!generatedReview.ok) {
        throw new Error("Review generation failed");
      }

      setGraphData(energyData.graph_points || []);
      setPeak(energyData.peak || null);

      const reviewData = await generatedReview.json();
      setReview(reviewData);
      console.log(reviewData);
    } catch (error) {
      console.error("Failed to analyze song:", error);
      setError(
        "Could not analyze song. Make sure the local backend is running.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <span className="brand-mark">
          <Waveform />
          SongRater
        </span>
        <h1>Know your track's signal.</h1>
        <p>
          Analyze your song locally — energy curve, peak moment, and a full
          critical read. Nothing leaves your machine unless you choose to
          publish it.
        </p>
      </section>

      <section className="upload-card">
        <input
          type="file"
          accept="audio/*"
          onChange={(event) => setFile(event.target.files[0])}
        />

        <input
          type="text"
          placeholder="Optional lyrics"
          value={lyrics}
          onChange={(event) => setLyrics(event.target.value)}
        />

        <button onClick={analyzeSong} disabled={!file || loading}>
          {loading ? "Analyzing signal…" : "Analyze song"}
        </button>
      </section>

      <section className="chart-card">
        <h2>Energy overview</h2>

        {graphData.length === 0 ? (
          <p className="empty-state">
            No input detected. Upload a track to see its energy curve.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={420}>
            <LineChart data={graphData}>
              <defs>
                <linearGradient id="rawGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f7cff" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#4f7cff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1f2c52" strokeDasharray="3 3" />
              <XAxis
                dataKey="time"
                type="number"
                domain={["dataMin", "dataMax"]}
                tickFormatter={formatTime}
                stroke="#5f6b93"
                tick={{ fill: "#9aa5c7", fontSize: 12 }}
                label={{
                  value: "Time",
                  position: "insideBottom",
                  offset: -5,
                  fill: "#5f6b93",
                }}
              />
              <YAxis
                stroke="#5f6b93"
                tick={{ fill: "#9aa5c7", fontSize: 12 }}
                label={{
                  value: "Energy",
                  angle: -90,
                  position: "insideLeft",
                  fill: "#5f6b93",
                }}
              />
              <Tooltip content={<ChartTooltip />} />

              <Line
                type="monotone"
                dataKey="energy"
                name="Raw energy"
                dot={false}
                stroke="#4f7cff"
                strokeOpacity={0.3}
              />

              <Line
                type="monotone"
                dataKey="smoothed_energy"
                name="Smoothed energy"
                dot={false}
                stroke="#7d9fff"
                strokeWidth={2.5}
              />

              {peak && (
                <ReferenceLine
                  x={peak.mid_time}
                  label={{
                    value: `Peak ${formatTime(peak.mid_time)}`,
                    position: "insideTopLeft",
                    fill: "#ffb454",
                    fontSize: 12,
                  }}
                  strokeDasharray="4 4"
                  stroke="#ffb454"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </section>
      {error && (
        <section className="error-card">
          <p>{error}</p>
        </section>
      )}
      {review && (
        <section className="review-card">
          <div className="rating-header">
            <ScoreGauge score={review.rating_out_of_100} />

            <div>
              <h2>Song review</h2>
              <p className="mood">{review.mood}</p>
            </div>
          </div>

          <p className="review-text">{review.review}</p>
        </section>
      )}
      {review?.ratings && (
        <section className="ratings-card">
          <h2>Ratings</h2>

          {Object.entries(review.ratings).map(([category, score]) => (
            <div className="rating-row" key={category}>
              <span>
                {category
                  .replaceAll("_", " ")
                  .replace(/\b\w/g, (letter) => letter.toUpperCase())}
              </span>

              <div className="rating-bar">
                <div className="rating-fill" style={{ width: `${score}%` }} />
              </div>

              <strong>{score}</strong>
            </div>
          ))}
        </section>
      )}
      {review && (
        <section className="feedback-grid">
          <div className="strength-card">
            <h3>Strengths</h3>

            <ul>
              {review.strengths?.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>

          <div className="weakness-card">
            <h3>Weaknesses</h3>

            {review.weaknesses?.length > 0 ? (
              <ul>
                {review.weaknesses.map((weakness, index) => (
                  <li key={index}>{weakness}</li>
                ))}
              </ul>
            ) : (
              <p>No major weaknesses detected.</p>
            )}
          </div>
        </section>
      )}
      {review?.lyrical_observations?.length > 0 && (
        <section className="themes-card">
          <h2>Lyrical themes</h2>

          {review.lyrical_observations.map((observation, index) => (
            <div className="theme" key={index}>
              <h3>{observation.theme}</h3>
              <p>{observation.reason}</p>
            </div>
          ))}
        </section>
      )}
      {review?.standout_moments?.length > 0 && (
        <section className="moments-card">
          <h2>Standout moments</h2>

          {review.standout_moments.map((moment, index) => (
            <div className="moment" key={index}>
              <strong>{moment.time}</strong>
              <span>Section {moment.section}</span>
              <p>{moment.reason}</p>
            </div>
          ))}
        </section>
      )}
      {review?.lyrics && (
        <details className="transcript-card">
          <summary>View transcription</summary>
          <p>{review.lyrics}</p>
        </details>
      )}
      {review?.transcript_warnings?.length > 0 && (
        <section className="warning-card">
          <h3>Transcription warnings</h3>

          <ul>
            {review.transcript_warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}

export default App;
