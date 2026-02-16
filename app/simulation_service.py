from __future__ import annotations

import random
import string
import time
from dataclasses import dataclass
from typing import Literal
from uuid import uuid4

from app.schemas import CallInput, CallSimulationResult, Transcript


@dataclass(frozen=True)
class Scenario:
    name: str
    tags: list[str]
    commitment_mode: Literal["full", "partial", "future", "uncertain", "aggressive_future"]
    user_opening_lines: list[str]
    user_commitment_lines: list[str]
    user_confirmation_lines: list[str]
    assistant_resolution_lines: list[str]


SCENARIOS = [
    Scenario(
        name="pago_total",
        tags=["contestada", "positiva", "pago_total", "compromiso_de_pago"],
        commitment_mode="full",
        user_opening_lines=[
            "Gracias por llamar, quiero resolver la deuda completa.",
            "Estoy dispuesto a liquidar hoy para cerrar el caso.",
            "Si, quiero dejar esta cuenta al dia con pago total.",
        ],
        user_commitment_lines=[
            "Confirmo pago total de {total_amount} para {payment_date}.",
            "Puedo liquidar {total_amount} en {payment_date}.",
            "Me comprometo a pagar todo el saldo ({total_amount}) en {payment_date}.",
        ],
        user_confirmation_lines=[
            "Confirmado, pago total en {payment_date}.",
            "Si, quedamos con pago completo para {payment_date}.",
            "De acuerdo, liquido el total en esa fecha.",
        ],
        assistant_resolution_lines=[
            "Perfecto, registro compromiso de pago total por {total_amount} en {payment_date}.",
            "Queda documentado pago completo de {total_amount} para {payment_date}.",
        ],
    ),
    Scenario(
        name="pago_parcial",
        tags=["contestada", "pago_parcial", "compromiso_de_pago", "negociacion"],
        commitment_mode="partial",
        user_opening_lines=[
            "No tengo el monto completo, pero si puedo hacer un abono.",
            "Quiero pagar, aunque por ahora solo me alcanza para una parte.",
            "Me interesa resolver, pero necesito comenzar con pago parcial.",
        ],
        user_commitment_lines=[
            "Puedo pagar {partial_amount} en {payment_date}.",
            "Me comprometo con un abono de {partial_amount} para {payment_date}.",
            "Solo puedo cubrir {partial_amount} en {payment_date}.",
        ],
        user_confirmation_lines=[
            "Confirmado: {partial_amount} en {payment_date}.",
            "Si, esa es mi propuesta de pago parcial.",
            "Quedamos con ese monto y esa fecha.",
        ],
        assistant_resolution_lines=[
            "Registro abono parcial de {partial_amount} para {payment_date}; el saldo restante queda en seguimiento.",
            "Queda documentado pago parcial de {partial_amount} en {payment_date}.",
        ],
    ),
    Scenario(
        name="intencion_futura",
        tags=["contestada", "intencion_futura", "indecision", "seguimiento_requerido"],
        commitment_mode="future",
        user_opening_lines=[
            "Si quiero pagar, pero hoy no puedo comprometer monto.",
            "Tengo intencion de pago, solo que no tengo fecha exacta aun.",
            "Necesito unos dias para confirmar cuanto podre cubrir.",
        ],
        user_commitment_lines=[
            "No puedo confirmar pago hoy; me comprometo a definir fecha y monto en {follow_up_date}.",
            "Mi intencion es pagar, y en {follow_up_date} le confirmo un compromiso claro.",
            "Necesito revisar flujo; en {follow_up_date} le doy monto y fecha.",
        ],
        user_confirmation_lines=[
            "Correcto, en {follow_up_date} confirmo el compromiso.",
            "Queda claro: hoy sin pago, con definicion para {follow_up_date}.",
            "Si, esa sera mi fecha para responder formalmente.",
        ],
        assistant_resolution_lines=[
            "Registro intencion futura sin fecha cerrada de pago; seguimiento pactado para {follow_up_date}.",
            "Queda documentado que hoy no hay pago confirmado y que usted definira condiciones en {follow_up_date}.",
        ],
    ),
    Scenario(
        name="negativa_sin_compromiso",
        tags=["contestada", "negativa", "sin_compromiso", "resistencia_pago"],
        commitment_mode="uncertain",
        user_opening_lines=[
            "No puedo pagar ahora y tampoco puedo prometer fecha.",
            "No tengo forma de comprometer pago en este momento.",
            "Hoy no voy a acordar monto ni dia.",
        ],
        user_commitment_lines=[
            "No puedo asumir compromiso de pago hoy.",
            "Prefiero no dejar fecha hasta que tenga claridad.",
            "Por ahora no hay compromiso, necesito revisar primero.",
        ],
        user_confirmation_lines=[
            "Si, dejelo como pendiente sin fecha definida.",
            "No puedo confirmar nada por ahora.",
            "Correcto, seguimos sin compromiso concreto.",
        ],
        assistant_resolution_lines=[
            "Registro llamada sin compromiso de pago. Se agenda seguimiento preventivo.",
            "Queda documentado que no se logro acuerdo ni fecha de pago en esta llamada.",
        ],
    ),
    Scenario(
        name="agresiva_con_insultos",
        tags=["contestada", "agresivo", "insultos", "intencion_futura", "contencion_emocional"],
        commitment_mode="aggressive_future",
        user_opening_lines=[
            "Siempre llaman a fastidiar, ya estoy cansado de esta cobranza.",
            "No me presione, esto me tiene harto.",
            "No quiero problemas, pero no voy a pagar hoy.",
        ],
        user_commitment_lines=[
            "No voy a pagar hoy; tal vez en {follow_up_date} revise un posible abono.",
            "No me comprometo ahora, pero en {follow_up_date} podria definir algo.",
            "Si mejora mi situacion, en {follow_up_date} le digo cuanto puedo pagar.",
        ],
        user_confirmation_lines=[
            "Anote eso: hoy no pago y en {follow_up_date} le confirmo.",
            "Si, en esa fecha podria revisar una opcion.",
            "Correcto, de momento no hay pago hoy.",
        ],
        assistant_resolution_lines=[
            "Entiendo su molestia y mantendre trato profesional. Registro seguimiento para {follow_up_date} sin compromiso inmediato.",
            "Dejo trazabilidad de tono hostil con intencion futura de revision en {follow_up_date}.",
        ],
    ),
]


def simulate_calls(rows: list[CallInput]) -> list[CallSimulationResult]:
    return [simulate_single_call(row) for row in rows]


def simulate_single_call(call_input: CallInput) -> CallSimulationResult:
    scenario = random.choice(SCENARIOS)
    room_name = call_input.room_name or _random_room_name()
    transcript_items, duration_seconds, function_result_tag = _build_transcript_items(call_input, scenario)
    tags = _merge_tags(scenario.tags, function_result_tag)

    return CallSimulationResult(
        room_name=room_name,
        transcript=Transcript(items=transcript_items),
        status="completed",
        call_tags=tags,
        participant_name=call_input.phone_number,
        call_duration_seconds=round(duration_seconds, 6),
    )


def _build_transcript_items(
    call_input: CallInput, scenario: Scenario
) -> tuple[list[dict], float, str]:
    total_amount = _format_amount(call_input.debt_amount)
    partial_amount_value = max(round(call_input.debt_amount * random.uniform(0.25, 0.55), 2), 1.0)
    partial_amount = _format_amount(partial_amount_value)
    payment_date = _pick_payment_date(call_input.due_date)
    follow_up_date = _pick_follow_up_date(call_input.due_date)

    text_ctx = {
        "total_amount": total_amount,
        "partial_amount": partial_amount,
        "payment_date": payment_date,
        "follow_up_date": follow_up_date,
    }

    opening_user = _render(random.choice(scenario.user_opening_lines), text_ctx)
    commitment_user = _render(random.choice(scenario.user_commitment_lines), text_ctx)
    confirmation_user = _render(random.choice(scenario.user_confirmation_lines), text_ctx)
    resolution_line = _render(random.choice(scenario.assistant_resolution_lines), text_ctx)

    greeting_user = random.choice(["Bueno.", "Hola.", "Si, quien habla?"])
    greeting_assistant = (
        f"Hola {call_input.name}, soy Laura del equipo de cobranza. "
        f"Tu deuda actual es de {total_amount} pesos y la fecha limite es {call_input.due_date}."
    )
    commitment_question = (
        "Busco un compromiso claro en esta llamada: fecha y monto exactos de pago total "
        "o de un abono inicial. Que propuesta puedes confirmar?"
    )
    clarify_question = (
        "Para dejarlo formal, confirmame el monto y la fecha exacta para registrar el acuerdo."
    )

    conversation = [
        ("user", greeting_user),
        ("assistant", greeting_assistant),
        ("user", opening_user),
        ("assistant", commitment_question),
        ("user", commitment_user),
        ("assistant", clarify_question),
        ("user", confirmation_user),
        ("assistant", resolution_line),
    ]

    if scenario.commitment_mode == "aggressive_future":
        conversation.insert(
            4,
            (
                "assistant",
                "Entiendo que estes molesto. Mantendre un tono profesional y te pido respeto para poder ayudarte.",
            ),
        )

    if scenario.commitment_mode in {"full", "partial"}:
        final_assistant_line = (
            "Gracias por confirmar. Si cumples ese compromiso, avanzaremos con la regularizacion sin escalar la gestion."
        )
    else:
        final_assistant_line = (
            "Gracias por la claridad. Dejo seguimiento activo para retomar en la fecha indicada."
        )
    conversation.append(("assistant", final_assistant_line))

    base_clock = time.time() - random.uniform(8.0, 30.0)
    timeline = base_clock
    first_start: float | None = None
    last_stop: float = timeline
    items: list[dict] = []

    items.append(
        {
            "id": _item_id(),
            "type": "agent_handoff",
            "new_agent_id": "outbound_caller",
        }
    )

    for role, text in conversation:
        if role == "user":
            item, timeline = _build_user_message_item(text, timeline)
        else:
            interrupted = random.random() < 0.14
            item, timeline = _build_assistant_message_item(text, timeline, interrupted=interrupted)
        started = item["metrics"]["started_speaking_at"]
        stopped = item["metrics"]["stopped_speaking_at"]
        first_start = started if first_start is None else min(first_start, started)
        last_stop = max(last_stop, stopped)
        items.append(item)

    function_call_item, function_output_item, function_result_tag = _build_function_items(
        scenario=scenario,
        total_amount=total_amount,
        partial_amount=partial_amount,
        payment_date=payment_date,
        follow_up_date=follow_up_date,
    )
    items.append(function_call_item)
    items.append(function_output_item)

    duration = max(last_stop - (first_start or last_stop), 0.0)
    return items, duration, function_result_tag


def _format_amount(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _render(template: str, context: dict[str, str]) -> str:
    return template.format(**context)


def _pick_payment_date(due_date: str) -> str:
    options = [due_date, f"un dia antes de {due_date}", f"el mismo {due_date}", "el proximo lunes"]
    return random.choice(options)


def _pick_follow_up_date(due_date: str) -> str:
    options = [
        "manana antes de las 5:00 p.m.",
        "en 48 horas",
        f"dos dias antes de {due_date}",
        "el proximo miercoles en la manana",
        "el cierre de esta semana",
    ]
    return random.choice(options)


def _random_room_name() -> str:
    token = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    return f"room-{token}"


def _item_id() -> str:
    return f"item_{uuid4().hex[:12]}"


def _call_id() -> str:
    return "call_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def _build_user_message_item(text: str, timeline: float) -> tuple[dict, float]:
    start = timeline + random.uniform(0.55, 1.9)
    stop = start + random.uniform(0.75, 4.2)
    item = {
        "id": _item_id(),
        "type": "message",
        "role": "user",
        "content": [text],
        "interrupted": False,
        "transcript_confidence": 1,
        "extra": {},
        "metrics": {
            "started_speaking_at": start,
            "stopped_speaking_at": stop,
            "transcription_delay": random.uniform(0.25, 0.45),
            "end_of_turn_delay": random.uniform(0.45, 0.7),
            "on_user_turn_completed_delay": random.uniform(0.0000004, 0.0000042),
        },
    }
    return item, stop


def _build_assistant_message_item(text: str, timeline: float, interrupted: bool) -> tuple[dict, float]:
    start = timeline + random.uniform(0.65, 2.2)
    stop = start + random.uniform(1.0, 6.8)
    item = {
        "id": _item_id(),
        "type": "message",
        "role": "assistant",
        "content": [text],
        "interrupted": interrupted,
        "extra": {},
        "metrics": {
            "started_speaking_at": start,
            "stopped_speaking_at": stop,
            "llm_node_ttft": random.uniform(0.6, 1.6),
            "tts_node_ttfb": random.uniform(0.4, 0.95),
            "e2e_latency": random.uniform(1.4, 3.6),
        },
    }
    return item, stop


def _build_function_items(
    scenario: Scenario,
    total_amount: str,
    partial_amount: str,
    payment_date: str,
    follow_up_date: str,
) -> tuple[dict, dict, str]:
    call_id = _call_id()

    if scenario.commitment_mode == "full":
        fn_name = "confirm_payment_custom"
        arguments = {"payment_amount": total_amount, "payment_date": payment_date}
        output = "full_payment_confirmed"
        tag = "pago_total"
    elif scenario.commitment_mode == "partial":
        fn_name = "confirm_payment_custom"
        arguments = {"payment_amount": partial_amount, "payment_date": payment_date}
        output = "custom_payment_confirmed"
        tag = "pago_parcial"
    elif scenario.commitment_mode in {"future", "aggressive_future"}:
        fn_name = "schedule_follow_up_custom"
        arguments = {"payment_amount": "to_define", "payment_date": follow_up_date}
        output = "follow_up_scheduled"
        tag = "seguimiento_requerido"
    else:
        fn_name = "schedule_follow_up_custom"
        arguments = {"payment_amount": "unknown", "payment_date": "pending_confirmation"}
        output = "follow_up_required"
        tag = "sin_compromiso"

    function_call_item = {
        "id": f"{_item_id()}/fnc_0",
        "type": "function_call",
        "call_id": call_id,
        "arguments": _json_string(arguments),
        "name": fn_name,
        "extra": {},
    }
    function_output_item = {
        "id": _item_id(),
        "type": "function_call_output",
        "name": fn_name,
        "call_id": call_id,
        "output": output,
        "is_error": False,
    }
    return function_call_item, function_output_item, tag


def _json_string(payload: dict[str, str]) -> str:
    parts = []
    for key, value in payload.items():
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        parts.append(f'"{key}":"{escaped}"')
    return "{" + ",".join(parts) + "}"


def _merge_tags(base_tags: list[str], extra_tag: str) -> list[str]:
    merged = list(base_tags)
    if extra_tag not in merged:
        merged.append(extra_tag)
    return merged
