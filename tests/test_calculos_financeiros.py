import pytest

from app import calcular_valor_futuro, gerar_evolucao, taxa_mensal_equivalente


def test_taxa_mensal_equivalente_recomposta_resulta_na_taxa_anual():
    taxa_mensal = taxa_mensal_equivalente(12)

    assert (1 + taxa_mensal) ** 12 - 1 == pytest.approx(0.12)


@pytest.mark.parametrize(
    ("inicial", "mensal", "taxa", "meses", "esperado"),
    [
        (1000, 100, 0, 12, 2200),
        (1000, 0, 0, 12, 1000),
        (0, 100, 0, 12, 1200),
    ],
)
def test_valor_futuro_sem_rendimento(inicial, mensal, taxa, meses, esperado):
    assert calcular_valor_futuro(inicial, mensal, taxa, meses) == pytest.approx(esperado)


def test_valor_futuro_com_taxa_positiva_e_aportes_no_fim_do_mes():
    taxa_mensal = taxa_mensal_equivalente(12)
    esperado = 1000 * (1 + taxa_mensal) ** 12
    esperado += 100 * (((1 + taxa_mensal) ** 12 - 1) / taxa_mensal)

    assert calcular_valor_futuro(1000, 100, 12, 12) == pytest.approx(esperado)


def test_evolucao_mensal_inclui_saldo_inicial_e_aporte_apos_rendimento():
    taxa_mensal = taxa_mensal_equivalente(12)

    evolucao = gerar_evolucao(1000, 100, 12, 2)

    assert evolucao == pytest.approx([
        {"mes": 0, "aportes": 1000.0, "saldo": 1000.0},
        {"mes": 1, "aportes": 1100.0, "saldo": 1000 * (1 + taxa_mensal) + 100},
        {
            "mes": 2,
            "aportes": 1200.0,
            "saldo": (1000 * (1 + taxa_mensal) + 100) * (1 + taxa_mensal) + 100,
        },
    ])


def test_ultima_linha_da_evolucao_corresponde_ao_valor_futuro():
    evolucao = gerar_evolucao(2500, 150, 8, 24)

    assert evolucao[-1]["mes"] == 24
    assert evolucao[-1]["saldo"] == pytest.approx(
        calcular_valor_futuro(2500, 150, 8, 24)
    )
