import React, { useState } from "react";
import ConnectionForm from "./components/ConnectionForm";
import Converter from "./components/Converter";

export default function App() {
  const [tab, setTab] = useState("convert");

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1>BTEQ → BigQuery Converter</h1>
          <p className="muted">Uses BigQuery Translator first, AI fallback if needed.</p>
        </div>
        <nav className="tabs">
          <button className={tab === "convert" ? "tab active" : "tab"} onClick={() => setTab("convert")}>
            Convert
          </button>
          <button className={tab === "settings" ? "tab active" : "tab"} onClick={() => setTab("settings")}>
            Connection
          </button>
        </nav>
      </header>

      {tab === "settings" ? (
        <ConnectionForm onSaved={() => setTab("convert")} />
      ) : (
        <Converter />
      )}
    </div>
  );
}