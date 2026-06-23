"""
utils/helpers.py
Funções auxiliares de formatação e utilitários gerais.
"""

from datetime import datetime


def formatar_data_br(dt) -> str:
    """Formata um datetime ou string ISO para o padrão brasileiro."""
    if not dt:
        return "—"
    if isinstance(dt, str):
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(dt, fmt)
                break
            except ValueError:
                continue
        if isinstance(dt, str):
            return dt  # retorna como está se não parsear
    return dt.strftime("%d/%m/%Y às %H:%M")


def formatar_data_curta(dt) -> str:
    """Retorna apenas a data no formato DD/MM/AAAA."""
    if not dt:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", ""))
        except Exception:
            return dt
    return dt.strftime("%d/%m/%Y")


def tamanho_legivel(bytes_size: int) -> str:
    """Converte tamanho em bytes para formato legível (KB, MB)."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


def truncar_texto(texto: str, max_chars: int = 100) -> str:
    """Trunca texto longo para exibição em listagens."""
    if not texto:
        return ""
    if len(texto) <= max_chars:
        return texto
    return texto[:max_chars].rstrip() + "…"


def status_emoji(status: str) -> str:
    """Retorna emoji representativo para cada status."""
    mapa = {
        "Recebida":                    "📥",
        "Em triagem":                  "🔍",
        "Encaminhada ao setor":        "📤",
        "Em análise":                  "🔬",
        "Aguardando resposta do cidadão": "⏳",
        "Resposta disponível":         "💬",
        "Concluída":                   "✅",
    }
    return mapa.get(status, "📋")


def status_cor(status: str) -> str:
    """Retorna cor CSS para badge de status."""
    mapa = {
        "Recebida":                    "#6c757d",
        "Em triagem":                  "#fd7e14",
        "Encaminhada ao setor":        "#0d6efd",
        "Em análise":                  "#6f42c1",
        "Aguardando resposta do cidadão": "#ffc107",
        "Resposta disponível":         "#20c997",
        "Concluída":                   "#198754",
    }
    return mapa.get(status, "#6c757d")
