import pytest

from app import Simulador


class FakeValue:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeTree:
    def __init__(self):
        self.rows = []

    def get_children(self):
        return list(self.rows)

    def delete(self, item):
        self.rows.remove(item)

    def insert(self, parent, index, iid=None, values=()):
        self.rows.append(iid if iid is not None else str(len(self.rows)))

    def selection(self):
        return ()


@pytest.fixture
def simulator():
    app = Simulador.__new__(Simulador)
    app.carteira = []
    app.resultado = None
    app.nome = FakeValue()
    app.alocacao = FakeValue()
    app.retorno = FakeValue()
    app.risco = FakeValue("Médio")
    app.inicial = FakeValue("1000")
    app.mensal = FakeValue("100")
    app.prazo = FakeValue("12")
    app.resumo = FakeValue()
    app.texto_analise = FakeValue()
    app.tabela_carteira = FakeTree()
    app.tabela_evolucao = FakeTree()
    return app
