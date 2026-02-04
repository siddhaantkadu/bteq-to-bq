import React from "react";

export default function ReportTable({ items }) {
  if (!items?.length) return null;

  return (
    <div className="card">
      <h2>Conversion Report</h2>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              <th>Lines</th>
              <th>Method</th>
              <th>OK</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it, idx) => (
              <tr key={idx}>
                <td>{it.line_start}-{it.line_end}</td>
                <td>{it.method}</td>
                <td>{it.ok ? "✅" : "❌"}</td>
                <td className="mono">{it.error || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted">
        Tip: If a statement fails dry-run, it will show with error message.
      </p>
    </div>
  );
}