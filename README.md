## LiveKit Mock - Simulador local por CSV

Aplicacion local para simular llamadas de cobranza tipo mock y ver la salida en JSON.

## Cambios clave

- Entrada por CSV.
- Transcript generado on-demand por cada fila.
- Sentimiento del usuario aleatorio (positivo, neutro, negativo, agresivo, con insultos, etc.).
- Agente siempre profesional y calmado.
- **Sin webhook** por ahora: todo se procesa localmente y se muestra en una consola JSON en la UI.

---

## Requisitos

- Python 3.11+

## Instalacion

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Abrir en navegador:

`http://localhost:8000`

---

## Formato de entrada CSV

Columnas requeridas (se aceptan alias comunes):

- `name` (persona)
- `room_id`
- `monto_deuda`
- `fecha limite`
- `telefono`

Ejemplo:

```csv
name,room_id,monto_deuda,fecha limite,telefono
Maria Lopez,room-001,12450.75,2026-03-05,+573001112233
Juan Perez,room-002,9800,2026-03-11,+573004445566
```

---

## Salida por cada llamada

```python
transcript: Optional[Transcript]
Outputs: {
  room_name: str
  call_tags: List[str]
  participant_name: str
  status: Optional[str]
  call_duration_seconds: Optional[float]
}
```

`call_tags` puede incluir etiquetas como:

- `positiva`
- `negativa`
- `neutra`
- `agresivo`
- `insultos`
- `compromiso_de_pago`
- `indecision`
- `seguimiento_requerido`
- `resistencia_pago`
- `estres_financiero`
- `negociacion`
- `posible_acuerdo`
- `alto_riesgo`
- `cliente_molesto`

---

## API usada por la UI

### `POST /api/simulate-csv`

- Content-Type: `multipart/form-data`
- Campo: `file` (archivo `.csv`)

Ejemplo con curl:

```bash
curl -X POST "http://localhost:8000/api/simulate-csv" \
  -F "file=@input.csv"
```

Respuesta ejemplo:

```json
{
  "input_rows": 1,
  "results": [
    {
      "transcript": {
        "language": "es",
        "sentiment_profile": "agresiva_con_insultos",
        "segments": [
          {
            "speaker": "agent",
            "text": "Buenas tardes, le saluda Laura del equipo de cobranzas...",
            "start_time_seconds": 0.48,
            "end_time_seconds": 2.73
          }
        ],
        "full_text": "..."
      },
      "Outputs": {
        "room_name": "room-001",
        "call_tags": ["agresivo", "insultos", "negativa", "intencion_futura"],
        "participant_name": "Maria Lopez",
        "status": "hostile_follow_up_required",
        "call_duration_seconds": 21.0
      }
    }
  ]
}
```
