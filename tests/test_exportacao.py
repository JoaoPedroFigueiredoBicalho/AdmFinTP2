import csv
from datetime import datetime
from unittest.mock import patch

from app import calcular_valor_futuro, gerar_evolucao


def preencher_resultado(simulator):
    simulator.carteira = [
        {"nome": "CDB & <Especial>", "alocacao": 100, "retorno": 8, "risco": "Baixo"}
    ]
    simulator.resultado = {
        "data": datetime(2026, 1, 2, 3, 4),
        "inicial": 1000,
        "mensal": 100,
        "meses": 2,
        "taxa": 8,
        "vf": calcular_valor_futuro(1000, 100, 8, 2),
        "aportado": 1200,
        "rendimento": calcular_valor_futuro(1000, 100, 8, 2) - 1200,
        "evolucao": gerar_evolucao(1000, 100, 8, 2),
        "comparacao": [{
            **simulator.carteira[0],
            "valor_futuro": calcular_valor_futuro(1000, 100, 8, 2),
        }],
    }


def test_exporta_evolucao_csv_com_separador_e_decimal_localizados(simulator, tmp_path):
    preencher_resultado(simulator)
    destino = tmp_path / "evolucao.csv"

    with patch("app.filedialog.asksaveasfilename", return_value=str(destino)), \
         patch("app.messagebox.showinfo"):
        simulator.exportar_evolucao()

    with destino.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.reader(arquivo, delimiter=";"))

    assert linhas[0] == [
        "Mês", "Aportes acumulados (R$)", "Saldo projetado (R$)",
        "Rendimento acumulado (R$)",
    ]
    assert len(linhas) == 4
    assert linhas[-1][0] == "2"
    assert "," in linhas[-1][2]


def test_exporta_csv_de_comparacao_com_todas_as_alternativas(simulator, tmp_path):
    preencher_resultado(simulator)
    destino = tmp_path / "carteira.csv"

    with patch("app.filedialog.asksaveasfilename", return_value=str(destino)), \
         patch("app.messagebox.showinfo"):
        simulator.exportar_carteira()

    with destino.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.reader(arquivo, delimiter=";"))

    assert linhas[0][0] == "Investimento"
    assert linhas[1][0] == "CDB & <Especial>"
    assert linhas[1][1:4] == ["100,00", "8,00", "Baixo"]


def test_gera_relatorio_html_completo_e_escapa_conteudo_de_usuario(
    simulator, tmp_path
):
    preencher_resultado(simulator)
    destino = tmp_path / "relatorio.html"

    with patch("app.filedialog.asksaveasfilename", return_value=str(destino)), \
         patch("app.messagebox.showinfo"):
        simulator.exportar_html()

    documento = destino.read_text(encoding="utf-8")
    assert '<html lang="pt-BR">' in documento
    assert "Retorno anual ponderado: 8.00%" in documento
    assert "CDB &amp; &lt;Especial&gt;" in documento
    assert "Metodologia e limitações" in documento


def test_exportacao_vazia_nao_cria_arquivo(simulator, tmp_path):
    preencher_resultado(simulator)

    with patch("app.filedialog.asksaveasfilename", return_value=""), \
         patch("app.messagebox.showinfo") as sucesso:
        simulator.exportar_evolucao()

    assert list(tmp_path.iterdir()) == []
    sucesso.assert_not_called()


def test_erro_de_escrita_e_reportado_ao_usuario(simulator):
    preencher_resultado(simulator)

    with patch("app.filedialog.asksaveasfilename", return_value="caminho.csv"), \
         patch("builtins.open", side_effect=OSError("sem permissão")), \
         patch("app.messagebox.showerror") as erro:
        simulator.exportar_evolucao()

    erro.assert_called_once()
