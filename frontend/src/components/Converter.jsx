import React, { useState } from "react";
import { createJob } from "../api";
import ReportTable from "./ReportTable";

export default function Converter() {
  const [input, setInput] = useState("");
  const [out, setOut] = useState("");
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const onUpload = async (file) => {
    const text = await file.text();
    setInput(text);
  };

  const convert = async () => {
    setBusy(true);
    setErr("");
    try {
      const resp = await createJob({
        script_text: input,
        source_dialect: "TERADATA",
        keep_bteq_cmds_as_comments: true
      });
      setOut(resp.translated_sql);
      setItems(resp.items || []);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const downloadSql = () => {
    const blob = new Blob([out], { type: "text/sql" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "translated_bigquery.sql";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="card">
        <h2>BTEQ Script</h2>

        <div className="row">
          <input
            type="file"
            accept=".bteq,.sql,.txt"
            onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
          />
          <button className="btn" onClick={convert} disabled={busy || !input.trim()}>
            {busy ? "Converting..." : "Convert"}
          </button>
        </div>

        <textarea
          className="ta"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Paste your BTEQ here..."
        />

        {err && <div className="error">{err}</div>}
      </div>

      <div className="card">
        <h2>BigQuery SQL Output</h2>
        <div className="row">
          <button className="btn" onClick={downloadSql} disabled={!out.trim()}>
            Download .sql
          </button>
        </div>
        <textarea className="ta mono" value={out} readOnly placeholder="Output will appear here..." />
      </div>

      <ReportTable items={items} />
    </>
  );
}