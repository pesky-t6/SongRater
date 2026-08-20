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

      setGraphData(energyData.graph_points || []);
      setPeak(energyData.peak || null);

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

      const reviewData = await generatedReview.json();
      setReview(reviewData);
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
        <h1>SongRater</h1>
        <p>
          Analyze your song locally. Nothing is uploaded unles you choose to
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
          {loading ? "Analyzing Song..." : "Analyze Song"}
        </button>
      </section>

      <section className="chart-card">
        <h2>Energy overview</h2>

        {graphData.length === 0 ? (
          <p className="empty-state">Upload a song to see its energy curve.</p>
        ) : (
          <ResponsiveContainer width="100%" height={420}>
            <LineChart data={graphData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="time"
                type="number"
                domain={["dataMin", "dataMax"]}
                tickFormatter={formatTime}
                label={{ value: "Time", position: "insideBottom", offset: -5 }}
              />
              <YAxis
                label={{ value: "Energy", angle: -90, position: "insideLeft" }}
              />
              <Tooltip
                labelFormatter={(value) => `Time: ${formatTime(value)}`}
              />

              <Line
                type="monotone"
                dataKey="energy"
                name="Raw energy"
                dot={false}
                strokeOpacity={0.35}
              />

              <Line
                type="monotone"
                dataKey="smoothed_energy"
                name="Smoothed energy"
                dot={false}
                strokeWidth={2}
              />

              {peak && (
                <ReferenceLine
                  x={peak.mid_time}
                  label={{
                    value: `Peak ${formatTime(peak.mid_time)}`,
                    position: "insideTopLeft",
                    fill: "green",
                  }}
                  strokeDasharray="4 4"
                  stroke="green"
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
            <div className="overall-rating">
              {review.rating_out_of_100}
              <span>/100</span>
            </div>

            <div>
              <h2>Song Review</h2>
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
          <h2>Lyrical Themes</h2>

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
          <h2>Standout Moments</h2>

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
          <h3>Transcription Warnings</h3>

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
