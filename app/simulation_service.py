from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from app.schemas import CallInputRow, CallSimulationResult, Transcript, TranscriptSegment


@dataclass(frozen=True)
class Scenario:
    name: str
    tags: list[str]
    status: str
    commitment_mode: Literal[
        "acuerdo_total",
        "acuerdo_parcial",
        "intencion_sin_fecha",
        "intencion_futura",
        "hostil_con_intencion_futura",
    ]
    user_opening_lines: list[str]
    user_commitment_lines: list[str]
    user_confirmation_lines: list[str]
    agent_resolution_lines: list[str]


AGENT_OPENING_LINES = [
    "Buenas tardes, le saluda Laura del equipo de cobranzas. Esta llamada es para regularizar su cuenta de forma respetuosa y encontrar un compromiso de pago.",
    "Gracias por atender. Mi objetivo es acordar con usted un plan claro y realista para resolver la deuda.",
]

AGENT_COMMITMENT_ASK_LINES = [
    "Para avanzar hoy necesito un compromiso concreto: fecha exacta de pago total o, si no es posible, fecha y monto de un primer abono.",
    "Le propongo cerrar esta llamada con un acuerdo verificable. Puede indicarme una fecha y un monto de pago?",
]

AGENT_RESPECT_CONTROL_LINES = [
    "Entiendo su molestia. Mantendre un tono profesional y le pido respeto para poder ayudarle de forma efectiva.",
    "Comprendo que la situacion incomoda. Mi intencion es resolver, no confrontar; por favor continuemos con respeto.",
]

SCENARIOS = [
    Scenario(
        name="positiva",
        tags=[
            "positiva",
            "compromiso_de_pago",
            "acuerdo_total",
            "colaborativo",
            "cierre_exitoso",
        ],
        status="commitment_registered",
        commitment_mode="acuerdo_total",
        user_opening_lines=[
            "Gracias por llamar. Si quiero ponerme al dia y cerrar esta deuda.",
            "De acuerdo, quiero resolver esto hoy y evitar mas recargos.",
            "Estoy dispuesto a ordenar el pago y dejarlo solucionado.",
        ],
        user_commitment_lines=[
            "Me comprometo a pagar el total antes de la fecha limite, exactamente {fecha_compromiso}.",
            "Confirmo pago total de {monto_total} en {fecha_compromiso}.",
            "Si, pago completo en {fecha_compromiso} y envio comprobante por este medio.",
        ],
        user_confirmation_lines=[
            "Queda confirmado: pago total en {fecha_compromiso}.",
            "Correcto, en {fecha_compromiso} hago la transferencia completa.",
            "Confirmado, cumplo ese dia con el monto total.",
        ],
        agent_resolution_lines=[
            "Perfecto, registro compromiso de pago total por {monto_total} para {fecha_compromiso}.",
            "Queda asentado acuerdo de pago completo en {fecha_compromiso}, sin cambios adicionales.",
        ],
    ),
    Scenario(
        name="neutra",
        tags=[
            "neutra",
            "intencion_sin_fecha",
            "indecision",
            "seguimiento_requerido",
            "solicita_informacion",
        ],
        status="follow_up_needed",
        commitment_mode="intencion_sin_fecha",
        user_opening_lines=[
            "Quiero pagar, pero hoy no puedo confirmar una fecha exacta.",
            "Tengo intencion de regularizar, aunque aun no se el dia de pago.",
            "Me interesa resolver, pero todavia no tengo liquidez definida.",
        ],
        user_commitment_lines=[
            "No puedo comprometer fecha de pago hoy; necesito revisar ingresos y confirmar el {fecha_seguimiento}.",
            "Mi intencion es pagar, pero aun no se cuando. Le confirmo una fecha concreta el {fecha_seguimiento}.",
            "Hoy no puedo fijar monto ni fecha; me comprometo a definirlo y responder el {fecha_seguimiento}.",
        ],
        user_confirmation_lines=[
            "Queda claro: hoy sin fecha de pago, y el {fecha_seguimiento} le confirmo compromiso concreto.",
            "Si, el {fecha_seguimiento} le doy fecha exacta y monto.",
            "Confirmado, le contacto el {fecha_seguimiento} con definicion final.",
        ],
        agent_resolution_lines=[
            "Registro intencion de pago sin fecha definitiva. Seguimiento pactado para el {fecha_seguimiento}.",
            "Dejo asentado que hoy no hay fecha concreta y que usted confirmara compromiso el {fecha_seguimiento}.",
        ],
    ),
    Scenario(
        name="negativa",
        tags=[
            "negativa",
            "resistencia_pago",
            "intencion_futura",
            "alto_riesgo",
            "seguimiento_requerido",
        ],
        status="escalation_review",
        commitment_mode="intencion_futura",
        user_opening_lines=[
            "Hoy no voy a pagar, tengo otras prioridades inmediatas.",
            "No puedo resolver en este momento, necesito mas tiempo.",
            "Ahora no tengo capacidad de pago y no quiero comprometer algo que no cumplire.",
        ],
        user_commitment_lines=[
            "No pago hoy. Mi intencion es revisar esto en {mes_futuro} y evaluar un abono inicial.",
            "No acepto pago inmediato; podria considerar un pago en {mes_futuro} si mejora mi flujo.",
            "Hoy no me comprometo con monto, pero mi intencion futura es retomar en {mes_futuro}.",
        ],
        user_confirmation_lines=[
            "Dejemoslo asi: sin pago hoy, posible gestion en {mes_futuro}.",
            "Repito: hoy no pago, y reviso nuevamente en {mes_futuro}.",
            "Confirmo que mi intencion es retomar el caso en {mes_futuro}.",
        ],
        agent_resolution_lines=[
            "Registro ausencia de compromiso inmediato y declaracion de intencion futura para {mes_futuro}.",
            "Queda documentado que hoy no hay acuerdo de pago y que usted solicita retomar en {mes_futuro}.",
        ],
    ),
    Scenario(
        name="agresiva_con_insultos",
        tags=[
            "agresivo",
            "insultos",
            "negativa",
            "intencion_futura",
            "riesgo_quiebre_llamada",
            "contencion_emocional",
        ],
        status="hostile_follow_up_required",
        commitment_mode="hostil_con_intencion_futura",
        user_opening_lines=[
            "Siempre llaman a molestar, ya estoy cansado de ustedes.",
            "No soporto estas llamadas, me tienen harto con la cobranza.",
            "Dejen de insistir, esta gestion me parece abusiva.",
        ],
        user_commitment_lines=[
            "No voy a pagar hoy. Tal vez en {mes_futuro} revise si puedo hacer un abono.",
            "No me comprometo ahora; si decido pagar sera en {mes_futuro}.",
            "Hoy no hay pago. Si mejora mi situacion, en {mes_futuro} veo si pago algo.",
        ],
        user_confirmation_lines=[
            "Anote eso y no insistan antes: sin pago hoy, posible revision en {mes_futuro}.",
            "Ya dije mi postura: hoy no pago y vere en {mes_futuro}.",
            "Queda claro: ahora no, quizas en {mes_futuro}.",
        ],
        agent_resolution_lines=[
            "Registro interaccion hostil y ausencia de compromiso inmediato; posible revision del pago en {mes_futuro}.",
            "Dejo documentado que hoy no hay acuerdo y que usted menciona una posible gestion en {mes_futuro}.",
        ],
    ),
    Scenario(
        name="estres_financiero",
        tags=[
            "preocupacion",
            "estres_financiero",
            "acuerdo_parcial",
            "negociacion",
            "posible_acuerdo",
            "requiere_plan_pago",
        ],
        status="partial_commitment_registered",
        commitment_mode="acuerdo_parcial",
        user_opening_lines=[
            "Quiero pagar, pero no tengo capacidad para cubrir el total hoy.",
            "Estoy en estres financiero y necesito una opcion por etapas.",
            "Mi intencion es cumplir, solo que requiero fraccionar el pago.",
        ],
        user_commitment_lines=[
            "Me comprometo a un primer abono de {monto_abono} en {fecha_compromiso} y luego revisamos el saldo.",
            "Puedo pagar {monto_abono} en {fecha_compromiso}; el resto lo cubro con un plan.",
            "Confirmo abono inicial de {monto_abono} en {fecha_compromiso} para empezar a regularizar.",
        ],
        user_confirmation_lines=[
            "Confirmado: primer abono {monto_abono} en {fecha_compromiso}.",
            "Si, ese abono inicial queda comprometido en esa fecha.",
            "Queda claro, inicio con {monto_abono} en {fecha_compromiso}.",
        ],
        agent_resolution_lines=[
            "Registro acuerdo parcial: abono inicial de {monto_abono} para {fecha_compromiso} y seguimiento del saldo.",
            "Queda asentado compromiso parcial con primer pago de {monto_abono} en {fecha_compromiso}.",
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
    amount = _format_amount(row.monto_deuda)
    commitment_date = _pick_commitment_date(row.fecha_limite)
    followup_date = _pick_follow_up_date(row.fecha_limite)
    future_month = _pick_future_month()
    partial_payment = _format_amount(max(row.monto_deuda * random.uniform(0.2, 0.5), 1.0))

    text_ctx = {
        "monto_total": amount,
        "monto_abono": partial_payment,
        "fecha_compromiso": commitment_date,
        "fecha_seguimiento": followup_date,
        "mes_futuro": future_month,
    }

    opening_user = _render(random.choice(scenario.user_opening_lines), text_ctx)
    commitment_user = _render(random.choice(scenario.user_commitment_lines), text_ctx)
    confirmation_user = _render(random.choice(scenario.user_confirmation_lines), text_ctx)
    resolution_line = _render(random.choice(scenario.agent_resolution_lines), text_ctx)
    opening_agent = random.choice(AGENT_OPENING_LINES)
    commitment_ask = random.choice(AGENT_COMMITMENT_ASK_LINES)
    respect_control = random.choice(AGENT_RESPECT_CONTROL_LINES)

    lines = [
        ("agent", opening_agent),
        (
            "agent",
            f"Le contacto por la cuenta de {row.name}. El saldo pendiente es de {amount} con fecha limite {row.fecha_limite}.",
        ),
        ("user", opening_user),
        (
            "agent",
            "Gracias por compartir su situacion. Voy a explicarle opciones reales para evitar mayor mora.",
        ),
        (
            "agent",
            commitment_ask,
        ),
    ]

    if scenario.commitment_mode == "hostil_con_intencion_futura":
        lines.append(("agent", respect_control))

    lines.extend(
        [
            ("user", commitment_user),
            (
                "agent",
                "Entendido. Confirmo lo que acaba de indicar y necesito su validacion final para dejar trazabilidad.",
            ),
            ("user", confirmation_user),
            ("agent", resolution_line),
            (
                "agent",
                f"Registro de cierre: contacto {row.telefono}, estado {scenario.status}, siguiente control operativo segun lo acordado.",
            ),
        ]
    )

    if scenario.commitment_mode in {"acuerdo_total", "acuerdo_parcial"}:
        lines.append(
            (
                "agent",
                "Le agradezco la disposicion. Si cumple en la fecha indicada, podremos estabilizar su cuenta sin escalar la gestion.",
            )
        )
    else:
        lines.append(
            (
                "agent",
                "Gracias por la claridad. Daremos seguimiento puntual segun su intencion declarada para mantener la gestion ordenada.",
            )
        )

    current_time = 0.0
    segments: list[TranscriptSegment] = []
    for speaker, text in lines:
        pause = random.uniform(0.2, 0.8)
        duration = random.uniform(1.4, 3.1)
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


def _format_amount(value: float) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _render(template: str, context: dict[str, str]) -> str:
    return template.format(**context)


def _pick_commitment_date(fecha_limite: str) -> str:
    options = [
        f"antes del {fecha_limite}",
        f"el mismo {fecha_limite}",
        "proximo lunes",
        "proximo martes",
        "viernes de esta semana",
    ]
    return random.choice(options)


def _pick_follow_up_date(fecha_limite: str) -> str:
    options = [
        "manana antes de las 5:00 p.m.",
        "en 48 horas",
        f"dos dias antes del {fecha_limite}",
        "el proximo miercoles en la manana",
        "el cierre de esta semana",
    ]
    return random.choice(options)


def _pick_future_month() -> str:
    return random.choice(
        [
            "la primera semana del proximo mes",
            "la segunda quincena del proximo mes",
            "fin de mes",
            "el siguiente ciclo de pago",
        ]
    )
