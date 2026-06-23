"""
utils/validators.py
Validadores reutilizáveis: CPF, e-mail, texto de manifestação.
RF03 — CPF obrigatório em manifestação identificada.
"""

import re
from config.settings import MANIFESTACAO_MIN_CHARS, MANIFESTACAO_MAX_CHARS


# ── CPF ────────────────────────────────────────────────────────────────────────

def _cpf_digitos(cpf: str) -> str:
    """Remove máscara do CPF, retorna apenas dígitos."""
    return re.sub(r"\D", "", cpf)


def validar_cpf(cpf: str) -> tuple[bool, str]:
    """
    Valida CPF brasileiro usando o algoritmo oficial dos dois dígitos verificadores.

    Retorna (True, "") se válido, ou (False, mensagem_de_erro) se inválido.
    """
    if not cpf or not cpf.strip():
        return False, "CPF é obrigatório para manifestações identificadas."

    digitos = _cpf_digitos(cpf)

    if len(digitos) != 11:
        return False, "CPF deve conter 11 dígitos numéricos."

    # CPFs com todos os dígitos iguais são inválidos (ex.: 111.111.111-11)
    if len(set(digitos)) == 1:
        return False, "CPF inválido."

    # Validação do 1º dígito verificador
    soma = sum(int(d) * (10 - i) for i, d in enumerate(digitos[:9]))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    if int(digitos[9]) != digito1:
        return False, "CPF inválido."

    # Validação do 2º dígito verificador
    soma = sum(int(d) * (11 - i) for i, d in enumerate(digitos[:10]))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    if int(digitos[10]) != digito2:
        return False, "CPF inválido."

    return True, ""


def formatar_cpf(cpf: str) -> str:
    """Retorna o CPF formatado como XXX.XXX.XXX-XX."""
    d = _cpf_digitos(cpf)
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return cpf


def mascarar_cpf(cpf: str) -> str:
    """Mascara o CPF para exibição: XXX.***.***-XX"""
    d = _cpf_digitos(cpf)
    if len(d) == 11:
        return f"{d[:3]}.***.***.{d[-2:]}"
    return "***.***.***-**"


# ── E-mail ─────────────────────────────────────────────────────────────────────

_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida formato de e-mail.
    Retorna (True, "") se válido, ou (False, mensagem_de_erro) se inválido.
    """
    if not email or not email.strip():
        return False, "E-mail é obrigatório para manifestações identificadas."

    email = email.strip()
    if len(email) > 254:
        return False, "E-mail muito longo (máximo 254 caracteres)."

    if not _EMAIL_PATTERN.match(email):
        return False, "E-mail inválido. Use o formato: usuario@dominio.com"

    return True, ""


# ── Texto da Manifestação ──────────────────────────────────────────────────────

def validar_texto_manifestacao(texto: str) -> tuple[bool, str]:
    """
    Valida o texto principal da manifestação.
    Mínimo: MANIFESTACAO_MIN_CHARS caracteres.
    Máximo: MANIFESTACAO_MAX_CHARS caracteres.
    """
    if not texto or not texto.strip():
        return False, "A descrição da manifestação não pode estar vazia."

    texto = texto.strip()

    if len(texto) < MANIFESTACAO_MIN_CHARS:
        return (
            False,
            f"A descrição deve ter pelo menos {MANIFESTACAO_MIN_CHARS} caracteres "
            f"(atual: {len(texto)}).",
        )

    if len(texto) > MANIFESTACAO_MAX_CHARS:
        return (
            False,
            f"A descrição não pode exceder {MANIFESTACAO_MAX_CHARS} caracteres "
            f"(atual: {len(texto)}).",
        )

    return True, ""


def validar_assunto(assunto: str, obrigatorio: bool = True) -> tuple[bool, str]:
    """Valida o campo de assunto/resumo."""
    if not assunto or not assunto.strip():
        if obrigatorio:
            return False, "O assunto é obrigatório."
        return True, ""

    assunto = assunto.strip()
    if len(assunto) < 5:
        return False, "O assunto deve ter pelo menos 5 caracteres."
    if len(assunto) > 120:
        return False, "O assunto não pode exceder 120 caracteres."

    return True, ""


def validar_nome(nome: str, obrigatorio: bool = True) -> tuple[bool, str]:
    """Valida o nome do cidadão."""
    if not nome or not nome.strip():
        if obrigatorio:
            return False, "O nome é obrigatório para manifestações identificadas."
        return True, ""

    nome = nome.strip()
    if len(nome) < 3:
        return False, "O nome deve ter pelo menos 3 caracteres."
    if len(nome) > 200:
        return False, "O nome não pode exceder 200 caracteres."

    # Apenas letras, espaços, acentos e hífens
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-\']+$", nome):
        return False, "O nome contém caracteres inválidos."

    return True, ""


def sanitizar_texto(texto: str) -> str:
    """Remove espaços excessivos e normaliza quebras de linha."""
    if not texto:
        return ""
    # Remove espaços no início/fim de cada linha e normaliza múltiplas linhas em branco
    linhas = [linha.strip() for linha in texto.strip().splitlines()]
    # Remove mais de 2 linhas em branco consecutivas
    resultado = []
    blank_count = 0
    for linha in linhas:
        if not linha:
            blank_count += 1
            if blank_count <= 2:
                resultado.append(linha)
        else:
            blank_count = 0
            resultado.append(linha)
    return "\n".join(resultado)
