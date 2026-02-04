import React, { useEffect, useState } from "react";
import { getConfig, saveConfig } from "../api";

export default function ConnectionForm({ onSaved }) {
  const [cfg, setCfg] = useState({
    gcp_project: "",
    gcp_location: "us",
    gcs_bucket: "",
    vertex_model: "gemini-1.5-pro",
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    getConfig()
      .then((c) => setCfg({
        gcp_project: c.gcp_project || "",
        gcp_location: c.gcp_location || "us",
        gcs_bucket: c.gcs_bucket || "",
        vertex_model: c.vertex_model || "gemini-1.5-pro",
      }))
      .catch(() => {});
  }, []);

  const update = (k, v) => setCfg((p) => ({ ...p, [k]: v }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      await saveConfig(cfg);
      setMsg("Saved");
      onSaved?.();
    } catch (err) {
      setMsg("Save failed" + err.message);
    }
  };

  return (
    <div className="card">
      <h2>Connection Settings</h2>
      <p className="muted">
        These are not credentials. Use GOOGLE_APPLICATION_CREDENTIALS or a default service account.
      </p>

      <form onSubmit={onSubmit} className="grid">
        <label>
          GCP Project
          <input
            value={cfg.gcp_project}
            onChange={(e) => update("gcp_project", e.target.value)}
            placeholder="my-gcp-project"
            required
          />
        </label>

        <label>
          Location
          <input
            value={cfg.gcp_location}
            onChange={(e) => update("gcp_location", e.target.value)}
            placeholder="us"
          />
        </label>

        <label>
          GCS Bucket (optional now, for future saving)
          <input
            value={cfg.gcs_bucket}
            onChange={(e) => update("gcs_bucket", e.target.value)}
            placeholder="my-bucket"
            required
          />
        </label>

        <label>
          Vertex Model (Gemini)
          <input
            value={cfg.vertex_model}
            onChange={(e) => update("vertex_model", e.target.value)}
            placeholder="gemini-1.5-pro"
          />
        </label>

        <button className="btn" type="submit">Save Settings</button>
        {msg && <div className="muted">{msg}</div>}
      </form>
    </div>
  );
}