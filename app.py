
"""
SIMULADOR DE GESTÃO DE INVESTIMENTOS
"""

import csv
import html
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


def taxa_mensal_equivalente(taxa_anual_percentual):
    """Converte taxa anual efetiva em taxa mensal efetiva equivalente."""
    taxa_anual = taxa_anual_percentual / 100
    return (1 + taxa_anual) ** (1 / 12) - 1


def calcular_valor_futuro(aporte_inicial, aporte_mensal, taxa_anual_percentual, meses):
    """
    Calcula o valor futuro com aporte inicial e aportes mensais no fim de cada mês.
    VF = P(1+i)^n + PMT * [((1+i)^n - 1) / i]
    """
    i = taxa_mensal_equivalente(taxa_anual_percentual)
    montante_inicial = aporte_inicial * ((1 + i) ** meses)

    # Se a taxa for zero, o valor futuro é apenas a soma dos aportes.
    if abs(i) < 1e-12:
        montante_mensal = aporte_mensal * meses
    else:
        montante_mensal = aporte_mensal * (((1 + i) ** meses - 1) / i)

    return montante_inicial + montante_mensal


def gerar_evolucao(aporte_inicial, aporte_mensal, taxa_anual_percentual, meses):
    """Calcula saldo e aportes acumulados para cada mês da simulação."""
    i = taxa_mensal_equivalente(taxa_anual_percentual)
    saldo = float(aporte_inicial)
    total_aportado = float(aporte_inicial)
    linhas = [{"mes": 0, "aportes": total_aportado, "saldo": saldo}]

    for mes in range(1, meses + 1):
        # Primeiro há rendimento sobre o saldo; depois entra o aporte do mês.
        saldo *= (1 + i)
        saldo += aporte_mensal
        total_aportado += aporte_mensal
        linhas.append({"mes": mes, "aportes": total_aportado, "saldo": saldo})

    return linhas


def numero(texto, nome_campo):
    """Converte entrada numérica, aceitando vírgula como separador decimal."""
    try:
        valor = float(str(texto).strip().replace(".", "").replace(",", "."))
    except ValueError:
        raise ValueError(f"Informe um número válido no campo '{nome_campo}'.")
    if not math.isfinite(valor):
        raise ValueError(f"Informe um número válido no campo '{nome_campo}'.")
    return valor


def moeda(valor):
    """Formata valor monetário no padrão brasileiro."""
    s = f"{valor:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


class Simulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Gestão de Investimentos")
        self.root.geometry("1150x800")
        self.root.minsize(950, 650)
        self.carteira = []
        self.resultado = None

        self.configurar_estilo()
        self.montar_interface()
        self.carregar_exemplos()
        self.atualizar_carteira()

    def configurar_estilo(self):
        """Configura estilos visuais dos componentes ttk."""
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("Arial", 18, "bold"))
        estilo.configure("Destaque.TLabel", font=("Arial", 10, "bold"))
        estilo.configure("Treeview", rowheight=25)
        estilo.configure("Treeview.Heading", font=("Arial", 9, "bold"))

    def montar_interface(self):
        """Cria a janela, as seções de entrada, resultados e relatórios."""
        cabecalho = ttk.Frame(self.root, padding=14)
        cabecalho.pack(fill="x")
        ttk.Label(
            cabecalho, text="Simulador de Gestão de Investimentos",
            style="Titulo.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Simulador de Gestão de Investimentos"
        ).pack(anchor="w", pady=(3, 0))

        # Canvas com barra de rolagem para acomodar a interface em telas menores.
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        barra = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.area = ttk.Frame(self.canvas, padding=(14, 2, 14, 14))
        self.area.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.area, anchor="nw")
        self.canvas.configure(yscrollcommand=barra.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.root.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units")
        )

        self.montar_parametros()
        self.montar_cadastro()
        self.montar_resultados()
        self.montar_relatorios()

    def montar_parametros(self):
        """Campos gerais da simulação."""
        quadro = ttk.LabelFrame(self.area, text="1. Parâmetros da simulação", padding=10)
        quadro.pack(fill="x", pady=(4, 9))

        self.inicial = self.campo(quadro, "Aporte inicial (R$)", "5000,00", 0)
        self.mensal = self.campo(quadro, "Aporte mensal (R$)", "300,00", 1)
        self.prazo = self.campo(quadro, "Prazo (meses)", "36", 2)

    def campo(self, pai, titulo, valor, coluna):
        """Cria um campo de texto com rótulo."""
        bloco = ttk.Frame(pai)
        bloco.grid(row=0, column=coluna, padx=6, sticky="ew")
        pai.columnconfigure(coluna, weight=1)
        ttk.Label(bloco, text=titulo).pack(anchor="w")
        entrada = ttk.Entry(bloco)
        entrada.insert(0, valor)
        entrada.pack(fill="x", pady=(4, 0))
        return entrada

    def montar_cadastro(self):
        """Formulário para cadastrar e remover alternativas de investimento."""
        quadro = ttk.LabelFrame(self.area, text="2. Carteira de investimentos", padding=10)
        quadro.pack(fill="x", pady=(0, 9))

        self.nome = tk.StringVar()
        self.alocacao = tk.StringVar()
        self.retorno = tk.StringVar()
        self.risco = tk.StringVar(value="Médio")

        campos = [
            ("Nome", self.nome, 0, 25),
            ("Alocação (%)", self.alocacao, 1, 13),
            ("Retorno anual (%)", self.retorno, 2, 15),
        ]
        for rotulo, variavel, coluna, largura in campos:
            bloco = ttk.Frame(quadro)
            bloco.grid(row=0, column=coluna, padx=5, sticky="ew")
            ttk.Label(bloco, text=rotulo).pack(anchor="w")
            ttk.Entry(bloco, textvariable=variavel, width=largura).pack(
                fill="x", pady=(4, 0)
            )

        bloco = ttk.Frame(quadro)
        bloco.grid(row=0, column=3, padx=5, sticky="ew")
        ttk.Label(bloco, text="Risco informado").pack(anchor="w")
        ttk.Combobox(
            bloco, textvariable=self.risco,
            values=["Baixo", "Médio", "Alto", "Não informado"],
            state="readonly", width=15
        ).pack(fill="x", pady=(4, 0))

        botoes = ttk.Frame(quadro)
        botoes.grid(row=0, column=4, padx=5, sticky="s")
        ttk.Button(botoes, text="Adicionar", command=self.adicionar).pack(fill="x")
        ttk.Button(
            botoes, text="Remover selecionado", command=self.remover
        ).pack(fill="x", pady=(4, 0))

        cols = ("nome", "alocacao", "retorno", "risco")
        self.tabela_carteira = ttk.Treeview(
            quadro, columns=cols, show="headings", height=5, selectmode="browse"
        )
        cabecalhos = {
            "nome": ("Investimento", 350),
            "alocacao": ("Alocação (%)", 140),
            "retorno": ("Retorno anual (%)", 160),
            "risco": ("Risco informado", 180),
        }
        for col, (titulo, largura) in cabecalhos.items():
            self.tabela_carteira.heading(col, text=titulo)
            self.tabela_carteira.column(col, width=largura, anchor="center")
        self.tabela_carteira.column("nome", anchor="w")

        # Utilizamos grid porque os demais componentes
        # deste LabelFrame também utilizam grid().
        self.tabela_carteira.grid(
            row=1,
            column=0,
            columnspan=5,
            sticky="ew",
            pady=(10, 3)
        )

        ttk.Label(
            quadro,
            text="As taxas e os níveis de risco são hipóteses editáveis para fins acadêmicos."
        ).grid(
            row=2,
            column=0,
            columnspan=5,
            sticky="w",
            pady=(2, 0)
        )

    def montar_resultados(self):
        """Área para acionar os cálculos e consultar resultados."""
        quadro = ttk.LabelFrame(self.area, text="3. Resultados da simulação", padding=10)
        quadro.pack(fill="both", expand=True, pady=(0, 9))
        ttk.Button(
            quadro, text="Calcular / Atualizar simulação", command=self.calcular
        ).pack(anchor="w", pady=(0, 9))

        self.resumo = tk.StringVar(value="Informe os dados e clique em calcular.")
        ttk.Label(
            quadro, textvariable=self.resumo, style="Destaque.TLabel",
            wraplength=1050, justify="left"
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(quadro, text="Evolução projetada:").pack(anchor="w")
        tabela_evolucao_frame = ttk.Frame(quadro)
        tabela_evolucao_frame.pack(fill="x", pady=(4, 10))
        cols = ("mes", "aportes", "saldo", "rendimento")
        self.tabela_evolucao = ttk.Treeview(
            tabela_evolucao_frame, columns=cols, show="headings", height=8
        )
        barra_evolucao = ttk.Scrollbar(
            tabela_evolucao_frame, orient="vertical",
            command=self.tabela_evolucao.yview
        )
        self.tabela_evolucao.configure(yscrollcommand=barra_evolucao.set)
        titulos = {
            "mes": "Mês",
            "aportes": "Aportes acumulados",
            "saldo": "Saldo projetado",
            "rendimento": "Rendimento acumulado",
        }
        for col, titulo in titulos.items():
            self.tabela_evolucao.heading(col, text=titulo)
            self.tabela_evolucao.column(col, width=220, anchor="center")
        self.tabela_evolucao.pack(side="left", fill="both", expand=True)
        barra_evolucao.pack(side="right", fill="y")

        self.texto_analise = tk.StringVar(value="")
        ttk.Label(
            quadro, textvariable=self.texto_analise, wraplength=1050,
            justify="left"
        ).pack(anchor="w")

    def montar_relatorios(self):
        """Botões de exportação dos arquivos que documentam a simulação."""
        quadro = ttk.LabelFrame(self.area, text="4. Exportação de relatórios", padding=10)
        quadro.pack(fill="x", pady=(0, 9))
        ttk.Button(
            quadro, text="Exportar evolução (CSV)", command=self.exportar_evolucao
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            quadro, text="Exportar carteira (CSV)", command=self.exportar_carteira
        ).pack(side="left", padx=8)
        ttk.Button(
            quadro, text="Gerar relatório completo (HTML)",
            command=self.exportar_html
        ).pack(side="left", padx=8)

        ttk.Label(
            self.area,
            text="Aviso: ferramenta educacional. Não consulta dados reais nem constitui recomendação.",
            foreground="#7a4b00"
        ).pack(anchor="w", pady=(2, 8))

    def carregar_exemplos(self):
        """Insere uma carteira inicial para facilitar a demonstração."""
        self.carteira = [
            {"nome": "Alternativa conservadora", "alocacao": 40.0,
             "retorno": 8.0, "risco": "Baixo"},
            {"nome": "Alternativa moderada", "alocacao": 35.0,
             "retorno": 10.0, "risco": "Médio"},
            {"nome": "Alternativa arrojada", "alocacao": 25.0,
             "retorno": 13.0, "risco": "Alto"},
        ]

    def atualizar_carteira(self):
        """Reflete a lista de investimentos na tabela da interface."""
        for item in self.tabela_carteira.get_children():
            self.tabela_carteira.delete(item)
        for indice, item in enumerate(self.carteira):
            self.tabela_carteira.insert(
                "", "end", iid=str(indice),
                values=(item["nome"], f'{item["alocacao"]:.2f}',
                        f'{item["retorno"]:.2f}', item["risco"])
            )

    def adicionar(self):
        """Valida e inclui uma alternativa na carteira."""
        try:
            nome = self.nome.get().strip()
            if not nome:
                raise ValueError("Informe o nome do investimento.")
            aloc = numero(self.alocacao.get(), "Alocação")
            ret = numero(self.retorno.get(), "Retorno anual")
            if not 0 <= aloc <= 100:
                raise ValueError("A alocação deve estar entre 0% e 100%.")
            if not -99 <= ret <= 1000:
                raise ValueError("O retorno anual deve estar entre -99% e 1000%.")

            self.carteira.append({
                "nome": nome, "alocacao": aloc,
                "retorno": ret, "risco": self.risco.get()
            })
            self.nome.set("")
            self.alocacao.set("")
            self.retorno.set("")
            self.resultado = None
            self.atualizar_carteira()
            messagebox.showinfo("Cadastro", "Investimento adicionado.")
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))

    def remover(self):
        """Remove o item atualmente selecionado."""
        selecionado = self.tabela_carteira.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um investimento.")
            return
        del self.carteira[int(selecionado[0])]
        self.resultado = None
        self.atualizar_carteira()

    def validar_entradas(self):
        """Lê parâmetros e valida a soma das alocações."""
        inicial = numero(self.inicial.get(), "Aporte inicial")
        mensal = numero(self.mensal.get(), "Aporte mensal")
        try:
            meses = int(self.prazo.get().strip())
        except ValueError:
            raise ValueError("O prazo deve ser um número inteiro de meses.")

        if inicial < 0 or mensal < 0:
            raise ValueError("Os aportes não podem ser negativos.")
        if not 1 <= meses <= 600:
            raise ValueError("O prazo deve estar entre 1 e 600 meses.")
        if not self.carteira:
            raise ValueError("Cadastre pelo menos um investimento.")

        soma = sum(x["alocacao"] for x in self.carteira)
        if not math.isclose(soma, 100, rel_tol=0, abs_tol=1e-9):
            raise ValueError(f"As alocações precisam somar 100%. Soma atual: {soma:.2f}%.")
        return inicial, mensal, meses

    def calcular(self):
        """Executa a simulação e atualiza os indicadores e a tabela mensal."""
        try:
            inicial, mensal, meses = self.validar_entradas()

            # Média ponderada dos retornos conforme a participação de cada alternativa.
            taxa_ponderada = sum(
                x["alocacao"] / 100 * x["retorno"] for x in self.carteira
            )
            vf = calcular_valor_futuro(inicial, mensal, taxa_ponderada, meses)
            aportado = inicial + mensal * meses
            rendimento = vf - aportado
            evolucao = gerar_evolucao(inicial, mensal, taxa_ponderada, meses)

            # Simula também o cenário em que todo o dinheiro fosse para cada opção.
            comparacao = []
            for item in self.carteira:
                comparacao.append({
                    **item,
                    "valor_futuro": calcular_valor_futuro(
                        inicial, mensal, item["retorno"], meses
                    )
                })

            self.resultado = {
                "data": datetime.now(), "inicial": inicial, "mensal": mensal,
                "meses": meses, "taxa": taxa_ponderada, "vf": vf,
                "aportado": aportado, "rendimento": rendimento,
                "evolucao": evolucao, "comparacao": comparacao
            }

            self.resumo.set(
                f"Retorno anual ponderado: {taxa_ponderada:.2f}%   |   "
                f"Total aportado: {moeda(aportado)}   |   "
                f"Valor futuro estimado: {moeda(vf)}   |   "
                f"Rendimento estimado: {moeda(rendimento)}"
            )

            # Exibe até cerca de 13 pontos da trajetória para manter a tabela legível.
            for item in self.tabela_evolucao.get_children():
                self.tabela_evolucao.delete(item)
            passo = max(1, meses // 12)
            amostra = evolucao[::passo]
            if amostra[-1]["mes"] != evolucao[-1]["mes"]:
                amostra.append(evolucao[-1])
            for linha in amostra:
                self.tabela_evolucao.insert(
                    "", "end",
                    values=(
                        linha["mes"], moeda(linha["aportes"]),
                        moeda(linha["saldo"]),
                        moeda(linha["saldo"] - linha["aportes"])
                    )
                )

            maior = max(self.carteira, key=lambda x: x["retorno"])
            menor = min(self.carteira, key=lambda x: x["retorno"])
            self.texto_analise.set(
                f"Análise: a carteira apresenta retorno anual ponderado hipotético de "
                f"{taxa_ponderada:.2f}%. A alternativa com maior retorno informado é "
                f"'{maior['nome']}' ({maior['retorno']:.2f}% a.a.); a menor é "
                f"'{menor['nome']}' ({menor['retorno']:.2f}% a.a.). Maior retorno "
                f"não significa necessariamente melhor escolha: risco, prazo e liquidez "
                f"também devem ser considerados."
            )
            messagebox.showinfo("Simulação", "Cálculos realizados com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Não foi possível calcular", str(erro))

    def pronto_para_exportar(self):
        """Confirma que existe uma simulação válida antes de exportar."""
        if self.resultado is None:
            messagebox.showwarning(
                "Simulação necessária",
                "Calcule a simulação antes de exportar os relatórios."
            )
            return False
        return True

    def exportar_evolucao(self):
        """Exporta os dados mensais para CSV, com separador compatível com Excel."""
        if not self.pronto_para_exportar():
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("Arquivo CSV", "*.csv")],
            initialfile="evolucao_investimento.csv"
        )
        if not caminho:
            return
        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as arq:
                escritor = csv.writer(arq, delimiter=";")
                escritor.writerow([
                    "Mês", "Aportes acumulados (R$)", "Saldo projetado (R$)",
                    "Rendimento acumulado (R$)"
                ])
                for x in self.resultado["evolucao"]:
                    escritor.writerow([
                        x["mes"], f'{x["aportes"]:.2f}'.replace(".", ","),
                        f'{x["saldo"]:.2f}'.replace(".", ","),
                        f'{(x["saldo"] - x["aportes"]):.2f}'.replace(".", ",")
                    ])
            messagebox.showinfo("Exportação", "CSV de evolução salvo.")
        except OSError as erro:
            messagebox.showerror("Erro", str(erro))

    def exportar_carteira(self):
        """Exporta as premissas e os cenários individuais da carteira para CSV."""
        if not self.pronto_para_exportar():
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("Arquivo CSV", "*.csv")],
            initialfile="comparacao_investimentos.csv"
        )
        if not caminho:
            return
        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as arq:
                escritor = csv.writer(arq, delimiter=";")
                escritor.writerow([
                    "Investimento", "Alocação (%)", "Retorno anual (%)",
                    "Risco informado", "Valor futuro isolado (R$)"
                ])
                for x in self.resultado["comparacao"]:
                    escritor.writerow([
                        x["nome"], f'{x["alocacao"]:.2f}'.replace(".", ","),
                        f'{x["retorno"]:.2f}'.replace(".", ","),
                        x["risco"], f'{x["valor_futuro"]:.2f}'.replace(".", ",")
                    ])
            messagebox.showinfo("Exportação", "CSV da carteira salvo.")
        except OSError as erro:
            messagebox.showerror("Erro", str(erro))

    def exportar_html(self):
        """Gera relatório HTML completo, que pode ser aberto em qualquer navegador."""
        if not self.pronto_para_exportar():
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[("Relatório HTML", "*.html")],
            initialfile="relatorio_gestao_investimentos.html"
        )
        if not caminho:
            return

        r = self.resultado
        linhas_carteira = ""
        for x in r["comparacao"]:
            linhas_carteira += (
                "<tr>"
                f"<td>{html.escape(x['nome'])}</td><td>{x['alocacao']:.2f}%</td>"
                f"<td>{x['retorno']:.2f}%</td><td>{html.escape(x['risco'])}</td>"
                f"<td>{moeda(x['valor_futuro'])}</td></tr>"
            )

        linhas_evolucao = ""
        passo = max(1, r["meses"] // 12)
        amostra = r["evolucao"][::passo]
        if amostra[-1]["mes"] != r["evolucao"][-1]["mes"]:
            amostra.append(r["evolucao"][-1])
        for x in amostra:
            linhas_evolucao += (
                f"<tr><td>{x['mes']}</td><td>{moeda(x['aportes'])}</td>"
                f"<td>{moeda(x['saldo'])}</td></tr>"
            )

        data = r["data"].strftime("%d/%m/%Y %H:%M")
        documento = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>Relatório de Gestão de Investimentos</title>
<style>
body {{font-family:Arial,sans-serif;margin:36px;color:#20252b}}
h1,h2 {{color:#174a70}}
table {{border-collapse:collapse;width:100%;margin:14px 0 26px}}
th,td {{border:1px solid #cbd3da;padding:9px;text-align:left}}
th {{background:#eaf1f6}}
.aviso {{background:#fff6df;padding:12px;border-left:4px solid #d59a20}}
</style></head><body>
<h1>Relatório de Gestão de Investimentos</h1>
<p>Gerado em {data} — Simulador de Gestão de Investimentos</p>
<h2>1. Parâmetros</h2><ul>
<li>Aporte inicial: {moeda(r['inicial'])}</li>
<li>Aporte mensal: {moeda(r['mensal'])}</li>
<li>Prazo: {r['meses']} meses</li>
<li>Retorno anual ponderado: {r['taxa']:.2f}%</li></ul>
<h2>2. Resultado consolidado</h2><ul>
<li>Total aportado: {moeda(r['aportado'])}</li>
<li>Valor futuro estimado: {moeda(r['vf'])}</li>
<li>Rendimento estimado: {moeda(r['rendimento'])}</li></ul>
<h2>3. Comparação das alternativas</h2>
<table><tr><th>Investimento</th><th>Alocação</th><th>Retorno anual</th>
<th>Risco informado</th><th>Valor futuro isolado</th></tr>
{linhas_carteira}</table>
<h2>4. Evolução projetada</h2>
<table><tr><th>Mês</th><th>Aportes acumulados</th><th>Saldo projetado</th></tr>
{linhas_evolucao}</table>
<h2>5. Metodologia e limitações</h2>
<p>Foi utilizada capitalização composta mensal, com conversão da taxa anual efetiva
para taxa mensal equivalente. Os aportes mensais ocorrem ao final de cada mês.
O retorno da carteira é calculado pela média ponderada dos retornos informados.</p>
</body></html>"""

        try:
            with open(caminho, "w", encoding="utf-8") as arq:
                arq.write(documento)
            messagebox.showinfo("Relatório", "Relatório HTML gerado com sucesso.")
        except OSError as erro:
            messagebox.showerror("Erro", str(erro))


if __name__ == "__main__":
    janela = tk.Tk()
    app = Simulador(janela)
    janela.mainloop()
