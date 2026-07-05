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

  async function analyzeSong() {
    if (!file) return;

    setLoading(true);

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

      const data = await analyzedEnergy.json();

      setGraphData(data.graph_points || []);
      setPeak(data.peak || null);
    } catch (error) {
      console.error("Failed to analyze song:", error);
      alert("Could not analyze song. Make sure the local backend is running.");
    } finally {
      setLoading(false);
    }

    try {
      const generatedReview = await fetch(
        "http://127.0.0.1:8000/generate-review",
        {
          method: "POST",
          body: formData,
        },
      );

      const data = await generatedReview.json();
      console.log(data);
    } catch (error) {
      console.error("Failed to analyze song:", error);
      alert("Could not analyze song. Make sure the local backend is running.");
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
          {loading ? "Analyzing..." : "Analyze energy graph"}
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
    </main>
  );
}

export default App;
