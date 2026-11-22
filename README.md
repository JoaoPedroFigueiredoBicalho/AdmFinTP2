# Simulador de Gestão de Investimentos — Tkinter

Trabalho 2 — Administração Financeira (CAD 167).

## Objetivo
Aplicação desktop educacional para simular uma carteira, comparar alternativas
e observar o efeito de aportes, prazo, taxas hipotéticas e alocações no valor futuro.

## Funcionalidades
- Interface gráfica desktop com Tkinter/ttk.
- Captura de aporte inicial, aporte mensal e prazo.
- Cadastro e remoção de alternativas de investimento.
- Alocação percentual, retorno anual hipotético e risco informado.
- Validação para que as alocações somem 100%.
- Retorno anual ponderado e valor futuro com juros compostos.
- Evolução mensal e comparação isolada das alternativas.
- Exportação de evolução e carteira em CSV e relatório completo em HTML.

## Requisitos
- Python 3.10 ou superior recomendado.
- Tkinter (normalmente incluído na instalação padrão do Python).
- Não exige Streamlit, Pandas, Matplotlib ou bibliotecas externas.

Em algumas distribuições Linux, instale o pacote `python3-tk` pelo gerenciador
de pacotes da distribuição.

## Como executar
Abra o terminal na pasta do projeto e execute:

```bash
python app.py
```

No Windows, se necessário:

```bash
py app.py
```

A janela do programa será aberta no desktop. Não há navegador nem servidor web.

## Testes automatizados
Instale as dependências de desenvolvimento e execute a suíte:

```bash
python -m pip install -r requirements.txt
pytest -v
```

Para executar os testes com relatório de cobertura:

```bash
pytest --cov=app --cov-report=term-missing -v
```

## Como utilizar
1. Informe aporte inicial, aporte mensal e prazo.
2. Cadastre ou mantenha as alternativas de exemplo.
3. Garanta que a soma das alocações seja 100%.
4. Clique em **Calcular / Atualizar simulação**.
5. Analise os indicadores e a evolução mensal.
6. Use os botões para exportar os relatórios CSV e HTML.

## Fórmulas
Taxa mensal equivalente:

    im = (1 + ia) ** (1/12) - 1

Valor futuro com aporte inicial e aportes mensais no fim de cada mês:

    VF = P(1+im)^n + PMT * (((1+im)^n - 1) / im)

Se a taxa mensal for zero, VF é a soma dos aportes.

Retorno anual ponderado:

    Rp = soma(peso_j * retorno_j)