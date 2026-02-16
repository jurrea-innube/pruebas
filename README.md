## LiveKit Mock - Simulador local (JSON + CSV)

Servicio local para simular llamadas de cobranza y devolver un transcript con estructura tipo LiveKit.

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

UI local:

`http://localhost:8000`

---

## Entrada por API JSON (nuevo formato principal)

Endpoint:

`POST /api/simulate-call`

Body esperado:

```json
{
  "phone_number": "+524771367757",
  "name": "Carlos",
  "debt_amount": "2300",
  "due_date": "25-02-2026"
}
```

> `debt_amount` puede enviarse como string o numero.

---

## Salida EXACTA (estructura)

```json
{
  "room_name": "room-neZdGV5wnrtf",
  "transcript": {
    "items": [
      {
        "id": "item_4dc79f101ac5",
        "type": "agent_handoff",
        "new_agent_id": "outbound_caller"
      },
      {
        "id": "item_2ee681cb97eb",
        "type": "message",
        "role": "user",
        "content": ["Bueno."],
        "interrupted": false,
        "transcript_confidence": 1,
        "extra": {},
        "metrics": {
          "started_speaking_at": 1771181838.28,
          "stopped_speaking_at": 1771181838.53,
          "transcription_delay": 0.36,
          "end_of_turn_delay": 0.65,
          "on_user_turn_completed_delay": 0.0000014
        }
      },
      {
        "id": "item_7b3d3883f601",
        "type": "message",
        "role": "assistant",
        "content": ["Hola..."],
        "interrupted": false,
        "extra": {},
        "metrics": {
          "started_speaking_at": 1771181841.80,
          "stopped_speaking_at": 1771181842.50,
          "llm_node_ttft": 2.31,
          "tts_node_ttfb": 0.58,
          "e2e_latency": 3.27
        }
      },
      {
        "id": "item_50b36194fb86/fnc_0",
        "type": "function_call",
        "call_id": "call_d691el6lnift3qlthjc0",
        "arguments": "{\"payment_amount\":\"1000\",\"payment_date\":\"24-02-2026\"}",
        "name": "confirm_payment_custom",
        "extra": {}
      },
      {
        "id": "item_d0a6f433e44d",
        "type": "function_call_output",
        "name": "confirm_payment_custom",
        "call_id": "call_d691el6lnift3qlthjc0",
        "output": "custom_payment_confirmed",
        "is_error": false
      }
    ]
  },
  "status": "completed",
  "call_tags": ["contestada", "pago_parcial"],
  "participant_name": "+524771367757",
  "call_duration_seconds": 115.5064709186554
}
```

---

## Entrada por CSV (para pruebas)

Endpoint:

`POST /api/simulate-csv`

Columnas recomendadas:

- `phone_number`
- `name`
- `debt_amount`
- `due_date`

CSV ejemplo:

```csv
phone_number,name,debt_amount,due_date
+524771367757,Carlos,2300,25-02-2026
+573001112233,Maria,1250.5,10-03-2026
```

Respuesta:

```json
{
  "input_rows": 2,
  "results": [
    { "...": "mismo formato exacto de salida por llamada" }
  ]
}
```
