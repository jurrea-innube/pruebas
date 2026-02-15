from __future__ import annotations

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.csv_service import parse_csv_rows
from app.simulation_service import simulate_calls

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("livekit-mock")

app = FastAPI(title="LiveKit Mock CSV Simulator", version="0.2.0")


HTML_PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>LiveKit Mock - CSV Simulator</title>
    <style>
      :root {
        color-scheme: dark;
      }
      body {
        margin: 0;
        font-family: Arial, sans-serif;
        background: #0f172a;
        color: #e2e8f0;
      }
      .container {
        max-width: 980px;
        margin: 2rem auto;
        padding: 1rem;
      }
      .card {
        background: #111827;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem;
      }
      .title {
        margin-top: 0;
      }
      .hint {
        color: #94a3b8;
        margin-top: 0.5rem;
      }
      .row {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        margin: 1rem 0;
        flex-wrap: wrap;
      }
      input[type="file"] {
        background: #0b1220;
        border: 1px solid #334155;
        color: #e2e8f0;
        padding: 0.5rem;
        border-radius: 6px;
      }
      button {
        background: #2563eb;
        color: #ffffff;
        border: none;
        padding: 0.55rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
      }
      button:disabled {
        background: #1e3a8a;
        cursor: not-allowed;
      }
      .console {
        margin-top: 1rem;
        background: #020617;
        border: 1px solid #334155;
        border-radius: 8px;
        min-height: 340px;
        padding: 1rem;
        overflow: auto;
        white-space: pre-wrap;
        word-break: break-word;
        font-family: Consolas, Monaco, monospace;
        line-height: 1.45;
      }
      .ok {
        color: #22c55e;
      }
      .error {
        color: #f87171;
      }
    </style>
  </head>
  <body>
    <main class="container">
      <section class="card">
        <h1 class="title">LiveKit Mock - Simulador local por CSV</h1>
        <p class="hint">
          Suba un CSV con columnas: <b>name, room_id, monto_deuda, fecha limite, telefono</b>.
          El resultado JSON se mostrara abajo.
        </p>
        <div class="row">
          <input id="csvFile" type="file" accept=".csv,text/csv" />
          <button id="runBtn">Procesar CSV</button>
          <span id="status"></span>
        </div>
        <pre id="console" class="console">Esperando archivo CSV...</pre>
      </section>
    </main>
    <script>
      const runBtn = document.getElementById("runBtn");
      const csvFile = document.getElementById("csvFile");
      const statusEl = document.getElementById("status");
      const consoleEl = document.getElementById("console");

      const setStatus = (text, isError = false) => {
        statusEl.textContent = text;
        statusEl.className = isError ? "error" : "ok";
      };

      runBtn.addEventListener("click", async () => {
        if (!csvFile.files || csvFile.files.length === 0) {
          setStatus("Seleccione un archivo CSV", true);
          return;
        }

        runBtn.disabled = true;
        setStatus("Procesando...");
        consoleEl.textContent = "Generando simulacion...";

        try {
          const form = new FormData();
          form.append("file", csvFile.files[0]);
          const response = await fetch("/api/simulate-csv", {
            method: "POST",
            body: form
          });
          const payload = await response.json();
          if (!response.ok) {
            setStatus("Error al procesar CSV", true);
            consoleEl.textContent = JSON.stringify(payload, null, 2);
            return;
          }
          setStatus("Simulacion completada");
          consoleEl.textContent = JSON.stringify(payload, null, 2);
        } catch (error) {
          setStatus("Fallo de red o servidor", true);
          consoleEl.textContent = JSON.stringify({ error: String(error) }, null, 2);
        } finally {
          runBtn.disabled = false;
        }
      });
    </script>
  </body>
</html>
"""


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    return HTML_PAGE


@app.post("/api/simulate-csv")
async def simulate_csv(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    content = await file.read()
    try:
        rows = parse_csv_rows(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = simulate_calls(rows)
    logger.info("Simulated %s calls from %s", len(results), filename)

    categorized_results = []
    for result in results:
        data = result.model_dump()
        categorized_results.append(
            {
                "transcript": data["transcript"],
                "Outputs": {
                    "room_name": data["room_name"],
                    "call_tags": data["call_tags"],
                    "participant_name": data["participant_name"],
                    "status": data["status"],
                    "call_duration_seconds": data["call_duration_seconds"],
                },
            }
        )

    return {
        "input_rows": len(rows),
        "results": categorized_results,
    }
