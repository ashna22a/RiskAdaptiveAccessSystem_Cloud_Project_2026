"""
Inference for the Zero Trust risk engine.

The model was trained on ZTA-RAD's 34 behavioral features.
The app sends a 15-feature payload, which we map here using
sensible defaults for features we don't collect directly.
"""
import joblib
import pandas as pd

from config import MODEL_DIR, RISK_LABELS


_MODEL = None
_FEATURE_ORDER = None


def _load():
    global _MODEL, _FEATURE_ORDER
    if _MODEL is None:
        _MODEL = joblib.load(f"{MODEL_DIR}/random_forest.joblib")
        _FEATURE_ORDER = joblib.load(f"{MODEL_DIR}/feature_order.joblib")
    return _MODEL, _FEATURE_ORDER


def _app_to_zta(payload: dict) -> dict:
    """
    Map the app's 15-feature payload to ZTA-RAD's 34 training features.

    The model learns the risk boundary from behavioral patterns
    (logon, device, HTTP metrics). At inference time we approximate
    these metrics from the app-side signals we can collect.
    """
    hour = int(payload.get("hour", 12))
    is_off_hours = 1 if (hour < 6 or hour > 22) else 0
    distance = float(payload.get("location_distance_km", 0))
    logins = float(payload.get("login_frequency", 12))
    fails = int(payload.get("failed_attempts_24h", 0))

    return {
        # Logon metrics
        "computadores_distintos": 1 + int(distance > 100),
        "total_logons": int(logins),
        "total_logoffs": int(logins * 0.9),
        "hora_logon_mais_comum": hour,
        "hora_logoff_mais_comum": min(hour + 1, 23),
        "logons_fim_de_semana": int(logins * (0.2 if is_off_hours else 0.05)),
        "logons_dias_uteis": int(logins * (0.8 if not is_off_hours else 0.4)),
        "logons_fora_horario_comercial": int(logins * (0.4 if is_off_hours else 0.02)),
        "logons_em_horario_comercial": int(logins * (0.6 if not is_off_hours else 0.1)),
        "logons_janela_acesso": 0,
        "proporcao_pc_mais_usado": int(logins * 100) if distance < 100 else 30,
        # Device metrics
        "pcs_distintos_dispositivo": 1,
        "total_atividades_dispositivo": int(logins * 50),
        "connect_fora_horario_comercial": int(logins * (0.3 if is_off_hours else 0.05)),
        "connect_em_horario_comercial": int(logins * 20),
        "connect_fim_de_semana": 0,
        "connect_dias_uteis": int(logins * 20),
        "connect_janela_acesso": 0,
        "total_connect_dispositivo": int(logins * 40),
        "total_disconnect_dispositivo": int(logins * 38),
        "conexoes_sem_desconexao": 0 if distance < 100 else 1,
        # HTTP access metrics
        "sites_distintos_visitados": int(logins * 5),
        "total_acessos_http": int(logins * 20),
        "acessos_fora_horario_comercial": int(logins * (5 if is_off_hours else 1)),
        "acessos_em_horario_comercial": int(logins * 10),
        "acessos_fim_de_semana": 0,
        "acessos_janela_acesso": 0,
        "visita_sites_compras": 0,
        "visita_sites_noticias": 0,
        "visita_sites_entretenimento": 0,
        "tamanho_medio_urls": 50,
        "termos_sensiveis_detectados": fails * 2,
        "tamanho_medio_conteudo": 200,
        "diferenca_acessos_fora_dentro": int(abs(logins * (5 if is_off_hours else 1) - logins * 10)),
    }


def predict(payload: dict) -> dict:
    """Predict risk for a single app payload."""
    model, feature_order = _load()
    zta_features = _app_to_zta(payload)

    row = [zta_features.get(col, 0) for col in feature_order]
    df = pd.DataFrame([row], columns=feature_order)

    pred = int(model.predict(df)[0])
    probs = model.predict_proba(df)[0]

    return {
        "risk_level": pred,
        "recommendation": RISK_LABELS[pred],
        "confidence": float(max(probs)),
        "probabilities": {
            "allow": float(probs[0]) if len(probs) > 0 else 0.0,
            "challenge": float(probs[1]) if len(probs) > 1 else 0.0,
            "deny": float(probs[2]) if len(probs) > 2 else 0.0,
        },
    }
