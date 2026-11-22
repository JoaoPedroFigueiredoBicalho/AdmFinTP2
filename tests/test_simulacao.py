from unittest.mock import patch

import pytest

from app import calcular_valor_futuro


def test_calculo_ponderado_gera_resultado_e_compara_alternativas(simulator):
    simulator.carteira = [
        {"nome": "Conservador", "alocacao": 40, "retorno": 5, "risco": "Baixo"},
        {"nome": "Arrojado", "alocacao": 60, "retorno": 15, "risco": "Alto"},
    ]
    simulator.inicial.set("1000")
    simulator.mensal.set("100")
    simulator.prazo.set("12")

    with patch("app.messagebox.showinfo"):
        simulator.calcular()

    resultado = simulator.resultado
    assert resultado["taxa"] == pytest.approx(11)
    assert resultado["aportado"] == pytest.approx(2200)
    assert resultado["vf"] == pytest.approx(calcular_valor_futuro(1000, 100, 11, 12))
    assert resultado["rendimento"] == pytest.approx(resultado["vf"] - 2200)
    assert [item["nome"] for item in resultado["comparacao"]] == [
        "Conservador", "Arrojado"
    ]
    assert resultado["comparacao"][1]["valor_futuro"] > resultado["comparacao"][0]["valor_futuro"]
    assert len(resultado["evolucao"]) == 13
    assert resultado["evolucao"][-1]["saldo"] == pytest.approx(resultado["vf"])
    assert "11.00%" in simulator.resumo.get()
    assert "Arrojado" in simulator.texto_analise.get()


def test_falha_na_validacao_nao_substitui_resultado_previo(simulator):
    simulator.resultado = {"vf": 123}
    simulator.carteira = [
        {"nome": "A", "alocacao": 90, "retorno": 5, "risco": "Baixo"}
    ]

    with patch("app.messagebox.showerror") as erro:
        simulator.calcular()

    erro.assert_called_once()
    assert simulator.resultado == {"vf": 123}


def test_exige_simulacao_antes_de_exportar(simulator):
    with patch("app.messagebox.showwarning") as aviso:
        assert simulator.pronto_para_exportar() is False

    aviso.assert_called_once()


def test_remover_exige_item_selecionado(simulator):
    with patch("app.messagebox.showwarning") as aviso:
        simulator.remover()

    aviso.assert_called_once()
    assert simulator.carteira == []
