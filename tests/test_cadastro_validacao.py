import pytest
from unittest.mock import patch


def test_cadastro_adiciona_investimento_e_limpa_campos(simulator):
    simulator.nome.set("  CDB  ")
    simulator.alocacao.set("25,5")
    simulator.retorno.set("10,25")
    simulator.risco.set("Baixo")

    with patch("app.messagebox.showinfo") as sucesso:
        simulator.adicionar()

    assert simulator.carteira == [{
        "nome": "CDB", "alocacao": 25.5, "retorno": 10.25, "risco": "Baixo"
    }]
    assert simulator.nome.get() == ""
    assert simulator.alocacao.get() == ""
    assert simulator.retorno.get() == ""
    sucesso.assert_called_once()


@pytest.mark.parametrize(
    ("nome", "alocacao", "retorno"),
    [
        ("", "50", "10"),
        ("CDB", "", "10"),
        ("CDB", "50", ""),
        ("CDB", "inválido", "10"),
        ("CDB", "50", "inválido"),
        ("CDB", "-0,01", "10"),
        ("CDB", "100,01", "10"),
        ("CDB", "NaN", "10"),
        ("CDB", "50", "Infinity"),
        ("CDB", "50", "-99,01"),
        ("CDB", "50", "1000,01"),
    ],
)
def test_cadastro_rejeita_campos_obrigatorios_e_valores_invalidos(
    simulator, nome, alocacao, retorno
):
    simulator.nome.set(nome)
    simulator.alocacao.set(alocacao)
    simulator.retorno.set(retorno)

    with patch("app.messagebox.showerror") as erro:
        simulator.adicionar()

    assert simulator.carteira == []
    erro.assert_called_once()


@pytest.mark.parametrize(
    ("alocacoes", "esperado"),
    [
        ([100], True),
        ([0, 100], True),
        ([33.33, 33.33, 33.34], True),
        ([99.99], False),
        ([100.01], False),
        ([40, 35, 24], False),
    ],
)
def test_validacao_exige_soma_exata_de_100_por_cento(
    simulator, alocacoes, esperado
):
    simulator.carteira = [
        {"nome": f"Investimento {i}", "alocacao": valor, "retorno": 5, "risco": "Baixo"}
        for i, valor in enumerate(alocacoes)
    ]

    if esperado:
        assert simulator.validar_entradas() == (1000.0, 100.0, 12)
    else:
        with pytest.raises(ValueError, match="somar 100%"):
            simulator.validar_entradas()


@pytest.mark.parametrize(
    ("inicial", "mensal", "prazo", "mensagem"),
    [
        ("abc", "100", "12", "número válido"),
        ("NaN", "100", "12", "número válido"),
        ("1000", "Infinity", "12", "número válido"),
        ("-1", "100", "12", "não podem ser negativos"),
        ("1000", "-1", "12", "não podem ser negativos"),
        ("1000", "100", "1.5", "inteiro"),
        ("1000", "100", "0", "entre 1 e 600"),
        ("1000", "100", "601", "entre 1 e 600"),
    ],
)
def test_validacao_rejeita_parametros_da_simulacao(
    simulator, inicial, mensal, prazo, mensagem
):
    simulator.carteira = [
        {"nome": "A", "alocacao": 100, "retorno": 5, "risco": "Baixo"}
    ]
    simulator.inicial.set(inicial)
    simulator.mensal.set(mensal)
    simulator.prazo.set(prazo)

    with pytest.raises(ValueError, match=mensagem):
        simulator.validar_entradas()


def test_validacao_rejeita_carteira_vazia(simulator):
    with pytest.raises(ValueError, match="pelo menos um investimento"):
        simulator.validar_entradas()
