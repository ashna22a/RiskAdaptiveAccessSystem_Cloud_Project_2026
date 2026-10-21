# ZTA-RAD Dataset

This folder contains the raw and processed data used to train and evaluate the
Zero Trust Cloud Access Recommendation System.

The raw dataset is **not** committed to this repository. See "Getting the data"
below to download it.

---

## 1. Dataset Identity

| Attribute | Value |
|-----------|-------|
| **Name** | ZTA-RAD (Zero Trust Architecture — Risk Assessment Dataset) |
| **Source** | Mendeley Data |
| **Publisher** | Elsevier B.V. |
| **DOI** | [10.17632/d6hvsrxdts](https://doi.org/10.17632/d6hvsrxdts) |
| **Dataset URL** | https://data.mendeley.com/datasets/d6hvsrxdts/1 |
| **Published** | 2 September 2025 |
| **License** | See the "License" field on the Mendeley landing page before use |
| **Original derivation** | Derived and expanded from the CERT Insider Threat Dataset |

---

## 2. Purpose in This Project

ZTA-RAD provides labelled behavioural records of insider threat scenarios in
cloud environments. We use it to train and evaluate a Random Forest classifier
that predicts the access risk level (Low / Medium / High) for a given request.

The task modelled here is **three-class classification**:

| Class | ZTA-RAD label | Recommendation |
|-------|---------------|----------------|
| 0 | Baixo (Low) | ALLOW |
| 1 | Médio (Medium) | CHALLENGE_MFA |
| 2 | Alto (High) | DENY |

---

## 3. Dataset Structure

The raw CSV (`zta_rad.csv`) contains **39 columns** spanning four categories:

### Logon metrics (11 columns)
`computadores_distintos`, `total_logons`, `total_logoffs`, `hora_logon_mais_comum`,
`hora_logoff_mais_comum`, `logons_fim_de_semana`, `logons_dias_uteis`,
`logons_fora_horario_comercial`, `logons_em_horario_comercial`,
`logons_janela_acesso`, `proporcao_pc_mais_usado`

### Device metrics (10 columns)
`pcs_distintos_dispositivo`, `total_atividades_dispositivo`,
`connect_fora_horario_comercial`, `connect_em_horario_comercial`,
`connect_fim_de_semana`, `connect_dias_uteis`, `connect_janela_acesso`,
`total_connect_dispositivo`, `total_disconnect_dispositivo`,
`conexoes_sem_desconexao`

### HTTP access metrics (12 columns)
`sites_distintos_visitados`, `total_acessos_http`,
`acessos_fora_horario_comercial`, `acessos_em_horario_comercial`,
`acessos_fim_de_semana`, `acessos_janela_acesso`, `visita_sites_compras`,
`visita_sites_noticias`, `visita_sites_entretenimento`, `tamanho_medio_urls`,
`termos_sensiveis_detectados`, `tamanho_medio_conteudo`,
`diferenca_acessos_fora_dentro`

### Metadata (6 columns)
`user` (anonymised ID), `computador_mais_usado` (anonymised device ID),
`classe` (numeric class), `risco` (Portuguese label: Baixo/Médio/Alto),
`sintetico` (1 if the row is synthetic, 0 if observed)

---

## 4. Getting the Data

Because of the licensing terms on Mendeley Data, the raw CSV is **not**
committed to this repository. To reproduce the pipeline:

1. Visit https://data.mendeley.com/datasets/d6hvsrxdts/1
2. Accept the license and download the CSV (typically named
   `ZTA-RAD.csv` or `ZTA_RAD_dataset.csv`)
3. Place it at:
