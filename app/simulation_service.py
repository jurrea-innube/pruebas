from __future__ import annotations

import random
from dataclasses import dataclass

from app.schemas import CallInputRow, CallSimulationResult, Transcript, TranscriptSegment


@dataclass(frozen=True)
class Scenario:
    name: str
    tags: list[str]
    status: str
    user_lines: list[str]
    user_reactions: list[str]


AGENT_LINES = [
    "Buenas tardes, le saluda Laura del equipo de cobranzas. Le llamo para revisar su deuda pendiente y encontrar una solucion.",
    "Entiendo su situacion. Mi objetivo es ayudarle con una alternativa realista de pago.",
    "Podemos evaluar una fecha o un plan parcial para que no siga creciendo el atraso.",
    "Gracias por su tiempo. Voy a dejar registrado el acuerdo y el siguiente paso.",
]

SCENARIOS = [
    Scenario(
        name="positiva",
        tags=["positiva", "compromiso_de_pago", "colaborativo", "disposicion_acuerdo"],
        status="commitment_registered",
        user_lines=[
            "Gracias por llamar. Si, quiero ponerme al dia con la deuda.",
            "Me sirve hacer el pago antes de la fecha limite.",
            "Confirmo que voy a transferir y enviar comprobante.",
        ],
        user_reactions=[
            "Podria recordarme el monto exacto por favor?",
            "Listo, lo voy a programar hoy.",
            "Agradezco el trato, quedamos asi.",
        ],
    ),
    Scenario(
        name="neutra",
        tags=["neutra", "solicita_informacion", "indecision", "seguimiento_requerido"],
        status="follow_up_needed",
        user_lines=[
            "Estoy revisando mis cuentas, aun no tengo una decision.",
            "Necesito validar primero unos gastos antes de comprometerme.",
            "Por ahora solo quiero entender las opciones disponibles.",
        ],
        user_reactions=[
            "Si me envia el detalle, lo reviso hoy en la tarde.",
            "Prefiero confirmar manana para no fallar.",
            "Podemos hablar de nuevo despues de revisar mis ingresos.",
        ],
    ),
    Scenario(
        name="negativa",
        tags=["negativa", "resistencia_pago", "alto_riesgo", "cliente_molesto"],
        status="escalation_review",
        user_lines=[
            "No pienso pagar en este momento, tengo otras prioridades.",
            "Ya me llamaron varias veces y no voy a aceptar presion.",
            "No tengo intencion de resolver esto hoy.",
        ],
        user_reactions=[
            "No me interesa ningun plan por ahora.",
            "Le dije que no, no insista.",
            "Si quieren, vuelvan a llamar otro dia.",
        ],
    ),
    Scenario(
        name="agresiva_con_insultos",
        tags=[
            "agresivo",
            "insultos",
            "negativa",
            "riesgo_quiebre_llamada",
            "contencion_emocional",
        ],
        status="hostile_interaction",
        user_lines=[
            "Siempre molestando, esto es una verguenza. Dejen de fastidiar.",
            "Ustedes solo llaman para acosar, no sirven para nada.",
            "No me hables de deuda, ya estoy harto de ustedes.",
        ],
        user_reactions=[
            "No me interesa lo que diga, son unos abusivos.",
            "Si siguen llamando voy a colgarles siempre.",
            "No quiero escuchar mas, esto es ridiculo.",
        ],
    ),
    Scenario(
        name="estres_financiero",
        tags=[
            "preocupacion",
            "estres_financiero",
            "negociacion",
            "posible_acuerdo",
            "requiere_plan_pago",
        ],
        status="payment_plan_discussion",
        user_lines=[
            "Quiero pagar, pero perdi ingresos y no llego al total.",
            "Estoy preocupado por los intereses, necesito una salida.",
            "Me ayudaria dividir el monto para cumplir sin atrasarme mas.",
        ],
        user_reactions=[
            "Si lo hacemos en cuotas, podria sostenerlo.",
            "Estoy dispuesto a dejar un primer pago esta semana.",
            "Necesito que quede por escrito para organizarme.",
        ],
    ),
]


def simulate_calls(rows: list[CallInputRow]) -> list[CallSimulationResult]:
    return [simulate_single_call(row) for row in rows]


def simulate_single_call(row: CallInputRow) -> CallSimulationResult:
    scenario = random.choice(SCENARIOS)
    transcript = _build_transcript(row, scenario)
    total_duration = transcript.segments[-1].end_time_seconds if transcript.segments else 0.0

    return CallSimulationResult(
        room_name=row.room_id,
        call_tags=scenario.tags,
        participant_name=row.name,
        transcript=transcript,
        status=scenario.status,
        call_duration_seconds=float(int(round(total_duration))),
    )


def _build_transcript(row: CallInputRow, scenario: Scenario) -> Transcript:
    amount = f"{row.monto_deuda:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    opening_user = random.choice(scenario.user_lines)
    closing_user = random.choice(scenario.user_reactions)

    lines = [
        ("agent", AGENT_LINES[0]),
        (
            "agent",
            f"Le contacto por la cuenta de {row.name}, deuda actual de {amount}, con fecha limite {row.fecha_limite}.",
        ),
        ("user", opening_user),
        ("agent", AGENT_LINES[1]),
        (
            "agent",
            "Si le parece, revisamos una propuesta de pago para evitar mas recargos y cerrar este caso.",
        ),
        ("user", closing_user),
        ("agent", AGENT_LINES[2]),
        (
            "agent",
            f"Queda registrado el numero de contacto {row.telefono} para seguimiento. Mantendremos comunicacion respetuosa.",
        ),
        ("agent", AGENT_LINES[3]),
    ]

    current_time = 0.0
    segments: list[TranscriptSegment] = []
    for speaker, text in lines:
        pause = random.uniform(0.2, 0.9)
        duration = random.uniform(1.5, 3.6)
        start_time = current_time + pause
        end_time = start_time + duration
        current_time = end_time
        segments.append(
            TranscriptSegment(
                speaker=speaker,
                text=text,
                start_time_seconds=round(start_time, 3),
                end_time_seconds=round(end_time, 3),
            )
        )

    return Transcript(
        language="es",
        sentiment_profile=scenario.name,
        segments=segments,
        full_text=" ".join(segment.text for segment in segments),
    )
