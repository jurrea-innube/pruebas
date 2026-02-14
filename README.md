## LiveKit Mock - Simulador de transcripciones

Servicio API que simula el flujo de LiveKit para pruebas de integracion.

### Que hace

1. Recibe datos del usuario por HTTP.
2. Genera una transcripcion simulada con formato **LiveKit-like**.
   - Si hay `OPENAI_API_KEY`, la transcripcion se crea con OpenAI en tiempo real.
   - Si no hay API key o falla la llamada, usa un generador de respaldo.
3. Espera un tiempo aleatorio entre 1 y 10 segundos.
4. Envia la transcripcion a un webhook configurado.

---

## Requisitos

- Python 3.11+

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configura `.env`:

```env
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4.1-mini
DEFAULT_WEBHOOK_URL=https://tu-plataforma.com/webhook
WEBHOOK_TIMEOUT_SECONDS=20
```

> `DEFAULT_WEBHOOK_URL` es opcional si mandas `webhook_url` en cada request.

## Ejecutar

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoint principal

`POST /mock/livekit/transcription`

### Ejemplo de request

```json
{
  "call_id": "call_demo_001",
  "room_name": "room-demo",
  "webhook_url": "https://webhook.site/xxxx",
  "language": "es",
  "call_context": "Cliente quiere renegociar su plan mensual",
  "objectives": [
    "Entender motivo del cambio",
    "Proponer alternativa de plan"
  ],
  "turns": 8,
  "user": {
    "name": "Maria Lopez",
    "identity": "customer_123"
  },
  "agent": {
    "name": "Sofia",
    "identity": "agent_sofia"
  },
  "metadata": {
    "tenant_id": "acme",
    "campaign": "retencion_q1"
  }
}
```

### Ejemplo de uso con curl

```bash
curl -X POST "http://localhost:8000/mock/livekit/transcription" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://webhook.site/xxxx",
    "user": {"name": "Maria Lopez", "identity": "customer_123"}
  }'
```

### Estructura del payload enviado al webhook

```json
{
  "event": "room.transcription.final",
  "source": "livekit-mock",
  "callId": "call_xxx",
  "room": {"name": "mock-room-..."},
  "createdAt": "2026-02-14T12:00:00+00:00",
  "metadata": {},
  "transcription": {
    "language": "es",
    "segments": [
      {
        "id": "SG_...",
        "speaker": "user",
        "participantIdentity": "customer_123",
        "participantName": "Maria Lopez",
        "text": "Hola, ...",
        "language": "es",
        "startTime": 0.512,
        "endTime": 2.731,
        "final": true
      }
    ],
    "text": "Transcripcion completa..."
  }
}
```
