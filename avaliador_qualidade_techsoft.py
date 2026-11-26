"""
===========================================================================
 AVALIADOR DE QUALIDADE — TECHSOFT
 Trabalho Integrador — Qualidade de Software
 Feito pelo aluno Gabriel Robe Giza
===========================================================================

Escala de notas:
    0 — Não atende
    1 — Atende parcialmente
    2 — Atende em grande parte
    3 — Atende completamente

"""

import json
from builtins import (
    EOFError,
    KeyboardInterrupt,
    OSError,
    ValueError,
    all,
    any,
    dict,
    enumerate,
    input,
    int,
    isinstance,
    len,
    list,
    min,
    open,
    print,
    sorted,
    str,
    sum,
)
from datetime import datetime
from pathlib import Path


# ===========================================================================
# 1. CONFIGURAÇÕES E DADOS FIXOS
# ===========================================================================

# Pasta onde o programa está; os arquivos gerados ficam ao lado dele.
PASTA_DO_PROGRAMA = Path(__file__).resolve().parent
ARQUIVO_DADOS = PASTA_DO_PROGRAMA / "processos.json"
ARQUIVO_RELATORIO = PASTA_DO_PROGRAMA / "relatorio_qualidade.txt"

# Significado de cada nota.
CLASSIFICACOES = {
    0: "NÃO ATENDE",
    1: "ATENDE PARCIALMENTE",
    2: "ATENDE EM GRANDE PARTE",
    3: "ATENDE COMPLETAMENTE",
}

# Peso de cada criticidade: quanto maior, mais urgente tratar o processo.
PESO_CRITICIDADE = {
    "BAIXA": 1,
    "MÉDIA": 2,
    "ALTA": 3,
}

NOTA_MAXIMA = 3
NOTA_LIMITE_FRACO = 1  # notas 0 e 1 são consideradas fracas

# Recomendações por processo (baseadas nos problemas do cenário da TechSoft).
RECOMENDACOES = {
    "Requisitos": [
        "Centralizar todas as solicitações em uma única ferramenta (fim do WhatsApp)",
        "Registrar toda solicitação com número, data e solicitante",
        "Exigir aprovação formal do cliente antes do desenvolvimento",
    ],
    "Desenvolvimento": [
        "Definir um padrão de codificação único para a equipe",
        "Usar controle de versão com fluxo de branches padronizado",
        "Distribuir conhecimento dos módulos (evitar dependência de 1 pessoa)",
    ],
    "Revisão de código": [
        "Tornar a revisão de código obrigatória antes do merge",
        "Registrar evidências de revisão (checklist / comentários no PR)",
    ],
    "Testes": [
        "Padronizar os testes com casos de teste documentados",
        "Registrar a execução e o resultado de todos os testes",
        "Criar indicadores de defeitos (ex.: defeitos por versão)",
    ],
    "Implantação": [
        "Proibir implantação sem homologação aprovada",
        "Manter registro de qual versão cada cliente utiliza",
        "Criar checklist de implantação e plano de rollback",
    ],
    "Suporte": [
        "Registrar todos os chamados em sistema de tickets",
        "Investigar a causa raiz dos problemas em produção",
        "Medir tempo de atendimento e reincidência de chamados",
    ],
}

# Recomendação usada quando o processo não está no dicionário acima
# (por exemplo, um processo novo adicionado pelo usuário).
RECOMENDACAO_GENERICA = [
    "Documentar o processo e definir um responsável",
    "Registrar evidências de execução e criar um indicador de acompanhamento",
]

# Avaliação inicial da TechSoft, justificada pelo cenário do trabalho.
PROCESSOS_PADRAO = [
    {"nome": "Requisitos",        "nota": 1, "criticidade": "ALTA"},   # sem aprovação do cliente, pedidos por WhatsApp
    {"nome": "Desenvolvimento",   "nota": 1, "criticidade": "MÉDIA"},  # cada dev trabalha de um jeito
    {"nome": "Revisão de código", "nota": 0, "criticidade": "ALTA"},   # revisão não é obrigatória
    {"nome": "Testes",            "nota": 1, "criticidade": "ALTA"},   # testes feitos, mas sem registro
    {"nome": "Implantação",       "nota": 0, "criticidade": "ALTA"},   # implanta sem homologação
    {"nome": "Suporte",           "nota": 1, "criticidade": "MÉDIA"},  # causas raramente investigadas
]


# ===========================================================================
# 2. FUNÇÕES DE ANÁLISE (regras de qualidade)
# ===========================================================================

def classificar(nota):
    """Converte a nota (0 a 3) no texto da situação."""
    return CLASSIFICACOES.get(nota, "NOTA INVÁLIDA")


def calcular_media(processos):
    """Calcula a média das notas. Retorna 0 se a lista estiver vazia."""
    if not processos:
        return 0.0
    soma = sum(p["nota"] for p in processos)
    return soma / len(processos)


def calcular_prioridade(processo):
    """
    Pontuação de prioridade = (nota máxima - nota) x peso da criticidade.
    Quanto maior o resultado, mais urgente é melhorar o processo.
    Exemplo: nota 0 e criticidade ALTA -> (3 - 0) x 3 = 9 (máximo).
    """
    lacuna = NOTA_MAXIMA - processo["nota"]
    peso = PESO_CRITICIDADE.get(processo["criticidade"], 1)
    return lacuna * peso


def ordenar_por_prioridade(processos):
    """Retorna uma nova lista, do processo mais urgente para o menos urgente."""
    return sorted(processos, key=calcular_prioridade, reverse=True)


def identificar_fracos(processos):
    """Retorna os processos com nota 0 ou 1, já ordenados por prioridade."""
    fracos = [p for p in processos if p["nota"] <= NOTA_LIMITE_FRACO]
    return ordenar_por_prioridade(fracos)


def processo_mais_fraco(processos):
    """
    Retorna o processo mais fraco: o de menor nota.
    Em caso de empate, vence o de maior criticidade.
    """
    if not processos:
        return None
    return min(
        processos,
        key=lambda p: (p["nota"], -PESO_CRITICIDADE.get(p["criticidade"], 1)),
    )


def obter_recomendacoes(processo):
    """Retorna a lista de recomendações para um processo."""
    return RECOMENDACOES.get(processo["nome"], RECOMENDACAO_GENERICA)


# ===========================================================================
# 3. FUNÇÕES DE EXIBIÇÃO / RELATÓRIO
# ===========================================================================

LINHA_DUPLA = "=" * 50
LINHA_SIMPLES = "-" * 50


def montar_cabecalho(titulo):
    return f"{LINHA_DUPLA}\n{titulo}\n{LINHA_DUPLA}"


def montar_lista_processos(processos):
    """Monta o texto com nome, nota e situação de cada processo."""
    linhas = []
    for p in processos:
        linhas.append(p["nome"])
        linhas.append(f"Nota: {p['nota']}")
        linhas.append(f"Criticidade: {p['criticidade']}")
        linhas.append(f"Situação: {classificar(p['nota'])}")
        linhas.append("")
    return "\n".join(linhas)


def montar_relatorio(processos):
    """Monta o relatório final completo como texto (para exibir ou salvar)."""
    if not processos:
        return "Nenhum processo cadastrado."

    fracos = identificar_fracos(processos)
    mais_fraco = processo_mais_fraco(processos)
    media = calcular_media(processos)

    partes = [
        montar_cabecalho("AVALIADOR DE QUALIDADE — TECHSOFT"),
        f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}",
        "",
        montar_lista_processos(processos),
        LINHA_SIMPLES,
        "PROCESSOS PRIORITÁRIOS (nota 0 ou 1, por ordem de prioridade)",
        "",
    ]

    if fracos:
        for p in fracos:
            partes.append(
                f"- {p['nome']} (nota {p['nota']}, criticidade {p['criticidade']}, "
                f"prioridade {calcular_prioridade(p)})"
            )
    else:
        partes.append("- Nenhum processo fraco. Parabéns!")

    partes += ["", "RECOMENDAÇÕES", ""]
    for p in fracos:
        partes.append(f"[{p['nome']}]")
        for rec in obter_recomendacoes(p):
            partes.append(f"- {rec}")
        partes.append("")

    partes += [
        LINHA_SIMPLES,
        f"PROCESSO MAIS FRACO: {mais_fraco['nome']} (nota {mais_fraco['nota']})",
        f"MÉDIA GERAL: {media:.2f}",
        f"INTERPRETAÇÃO: {interpretar_media(media)}",
    ]
    return "\n".join(partes)


def interpretar_media(media):
    """Traduz a média em uma leitura simples de maturidade."""
    if media < 1.5:
        return "Baixa maturidade — processos dependem muito das pessoas."
    if media < 2.5:
        return "Maturidade intermediária — processos parcialmente definidos."
    return "Boa maturidade — processos definidos e com evidências."


# ===========================================================================
# 4. ENTRADA DE DADOS (com tratamento de erros)
# ===========================================================================

def ler_inteiro(mensagem, minimo, maximo):
    """Lê um número inteiro entre 'minimo' e 'maximo', repetindo até ser válido."""
    while True:
        texto = input(mensagem).strip()
        try:
            valor = int(texto)
        except ValueError:
            print(f"  Entrada inválida: digite um número inteiro.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"  Valor fora do intervalo: digite entre {minimo} e {maximo}.")


def ler_criticidade():
    """Lê a criticidade aceitando BAIXA, MÉDIA (ou MEDIA) e ALTA."""
    while True:
        texto = input("Criticidade (BAIXA / MÉDIA / ALTA): ").strip().upper()
        if texto == "MEDIA":
            texto = "MÉDIA"
        if texto in PESO_CRITICIDADE:
            return texto
        print("  Criticidade inválida.")


def escolher_processo(processos):
    """Mostra a lista numerada e devolve o processo escolhido."""
    for i, p in enumerate(processos, start=1):
        print(f"  {i}. {p['nome']} (nota atual: {p['nota']})")
    indice = ler_inteiro("Número do processo: ", 1, len(processos))
    return processos[indice - 1]


# ===========================================================================
# 5. ARQUIVOS (salvar e carregar)
# ===========================================================================

def processo_valido(p):
    """Confere se um dicionário lido do arquivo tem o formato correto."""
    return (
        isinstance(p, dict)
        and isinstance(p.get("nome"), str)
        and p.get("nota") in CLASSIFICACOES
        and p.get("criticidade") in PESO_CRITICIDADE
    )


def carregar_processos():
    """
    Carrega os processos de processos.json.
    Se o arquivo não existir ou estiver inválido, usa a avaliação padrão.
    """
    if not ARQUIVO_DADOS.exists():
        return [dict(p) for p in PROCESSOS_PADRAO]
    try:
        with open(ARQUIVO_DADOS, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if isinstance(dados, list) and dados and all(processo_valido(p) for p in dados):
            return dados
        print("Aviso: processos.json com formato inválido. Usando dados padrão.")
    except (OSError, json.JSONDecodeError) as erro:
        print(f"Aviso: não foi possível ler processos.json ({erro}). Usando dados padrão.")
    return [dict(p) for p in PROCESSOS_PADRAO]


def salvar_processos(processos):
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(processos, arquivo, ensure_ascii=False, indent=4)
        print(f"Dados salvos em: {ARQUIVO_DADOS.name}")
    except OSError as erro:
        print(f"Erro ao salvar os dados: {erro}")


def salvar_relatorio(processos):
    try:
        with open(ARQUIVO_RELATORIO, "w", encoding="utf-8") as arquivo:
            arquivo.write(montar_relatorio(processos))
        print(f"Relatório salvo em: {ARQUIVO_RELATORIO.name}")
    except OSError as erro:
        print(f"Erro ao salvar o relatório: {erro}")


# ===========================================================================
# 6. AÇÕES DO MENU
# ===========================================================================

def acao_listar(processos):
    print()
    print(montar_cabecalho("PROCESSOS AVALIADOS"))
    print(montar_lista_processos(processos))


def acao_relatorio(processos):
    print()
    print(montar_relatorio(processos))


def acao_prioridade(processos):
    print()
    print(montar_cabecalho("PROCESSOS POR ORDEM DE PRIORIDADE"))
    for posicao, p in enumerate(ordenar_por_prioridade(processos), start=1):
        print(f"{posicao}. {p['nome']:<20} nota {p['nota']}  "
              f"{p['criticidade']:<6} prioridade {calcular_prioridade(p)}")


def acao_alterar_nota(processos):
    print("\nQual processo deseja reavaliar?")
    processo = escolher_processo(processos)
    print("Notas: 0 = Não atende | 1 = Parcial | 2 = Grande parte | 3 = Completo")
    processo["nota"] = ler_inteiro("Nova nota (0 a 3): ", 0, 3)
    print(f"Nota de '{processo['nome']}' alterada para {processo['nota']} "
          f"({classificar(processo['nota'])}).")


def acao_adicionar(processos):
    nome = input("\nNome do novo processo: ").strip()
    if not nome:
        print("  Nome não pode ficar vazio.")
        return
    if any(p["nome"].lower() == nome.lower() for p in processos):
        print("  Já existe um processo com esse nome.")
        return
    nota = ler_inteiro("Nota (0 a 3): ", 0, 3)
    criticidade = ler_criticidade()
    processos.append({"nome": nome, "nota": nota, "criticidade": criticidade})
    print(f"Processo '{nome}' adicionado.")


def acao_restaurar(processos):
    processos.clear()
    processos.extend(dict(p) for p in PROCESSOS_PADRAO)
    print("Avaliação padrão da TechSoft restaurada.")


# ===========================================================================
# 7. MENU PRINCIPAL
# ===========================================================================

# Cada opção do menu aponta para (texto, função).
OPCOES_MENU = {
    "1": ("Listar processos e notas", acao_listar),
    "2": ("Mostrar relatório final", acao_relatorio),
    "3": ("Ver processos por prioridade", acao_prioridade),
    "4": ("Alterar nota de um processo", acao_alterar_nota),
    "5": ("Adicionar novo processo", acao_adicionar),
    "6": ("Salvar dados (processos.json)", salvar_processos),
    "7": ("Salvar relatório (relatorio_qualidade.txt)", salvar_relatorio),
    "8": ("Restaurar avaliação padrão", acao_restaurar),
}


def exibir_menu():
    print()
    print(montar_cabecalho("MENU — AVALIADOR DE QUALIDADE TECHSOFT"))
    for chave, (texto, _) in OPCOES_MENU.items():
        print(f"{chave}. {texto}")
    print("0. Sair")


def main():
    processos = carregar_processos()
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Encerrando o avaliador. Até logo!")
            break
        if opcao not in OPCOES_MENU:
            print("Opção inválida. Tente novamente.")
            continue
        _, funcao = OPCOES_MENU[opcao]
        funcao(processos)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrompido pelo usuário.")
