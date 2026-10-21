"""
Central configuration for the Zero Trust risk engine.

Two distinct feature schemas live in this file:
  1. APP_FEATURES     — the 15-feature payload the frontend sends
  2. ZTA_TRAIN_FEATURES — the 34 ZTA-RAD columns the model trains on

Inference (src/inference.py) maps the app schema → ZTA schema.
"""

# ---------------------------------------------------------------------------
# 1. Target
# ---------------------------------------------------------------------------
TARGET_COLUMN = "risk_level"

# Maps ZTA-RAD's Portuguese 'risco' values to integer classes
RISK_LABEL_MAP = {
    "baixo": 0, "low": 0, "allow": 0, "0": 0,
    "medio": 1, "médio": 1, "medium": 1, "challenge": 1, "challenge_mfa": 1, "1": 1,
    "alto": 2, "high": 2, "deny": 2, "critical": 2, "2": 2,
}

# Reverse map for display
RISK_LABELS = {0: "ALLOW", 1: "CHALLENGE_MFA", 2: "DENY"}

# ---------------------------------------------------------------------------
# 2. App-facing schema (what the frontend sends)
# ---------------------------------------------------------------------------
APP_CATEGORICAL_FEATURES = [
    "user_role",
    "service_type",
    "department",
    "access_method",
    "device_type",
]

APP_NUMERICAL_FEATURES = [
    "login_frequency",
    "session_duration",
    "time_since_last_login",
    "location_distance_km",
    "access_count_7d",
    "failed_attempts_24h",
    "session_requests",
    "is_off_hours",
    "location_mismatch",
    "device_mismatch",
]

APP_FEATURES = APP_CATEGORICAL_FEATURES + APP_NUMERICAL_FEATURES

# ---------------------------------------------------------------------------
# 3. ZTA-RAD training schema (raw columns used by the model)
# ---------------------------------------------------------------------------
ZTA_TRAIN_FEATURES = [
    # Logon metrics
    "computadores_distintos",
    "total_logons",
    "total_logoffs",
    "hora_logon_mais_comum",
    "hora_logoff_mais_comum",
    "logons_fim_de_semana",
    "logons_dias_uteis",
    "logons_fora_horario_comercial",
    "logons_em_horario_comercial",
    "logons_janela_acesso",
    "proporcao_pc_mais_usado",
    # Device metrics
    "pcs_distintos_dispositivo",
    "total_atividades_dispositivo",
    "connect_fora_horario_comercial",
    "connect_em_horario_comercial",
    "connect_fim_de_semana",
    "connect_dias_uteis",
    "connect_janela_acesso",
    "total_connect_dispositivo",
    "total_disconnect_dispositivo",
    "conexoes_sem_desconexao",
    # HTTP access metrics
    "sites_distintos_visitados",
    "total_acessos_http",
    "acessos_fora_horario_comercial",
    "acessos_em_horario_comercial",
    "acessos_fim_de_semana",
    "acessos_janela_acesso",
    "visita_sites_compras",
    "visita_sites_noticias",
    "visita_sites_entretenimento",
    "tamanho_medio_urls",
    "termos_sensiveis_detectados",
    "tamanho_medio_conteudo",
    "diferenca_acessos_fora_dentro",
]

# ---------------------------------------------------------------------------
# 4. Paths
# ---------------------------------------------------------------------------
RAW_DATA_PATH = "data/raw/zta_rad.csv"
PROCESSED_DIR = "data/processed"
MODEL_DIR = "models"
RANDOM_SEED = 42
