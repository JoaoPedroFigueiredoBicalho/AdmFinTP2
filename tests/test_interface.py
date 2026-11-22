from unittest.mock import patch

import app


class FakeWidget:
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.kwargs = kwargs
        self.managers = set()
        self.children = []
        self.rows = []
        self.configurations = []
        if parent is not None:
            parent.children.append(self)

    def pack(self, **kwargs):
        self.managers.add("pack")

    def grid(self, **kwargs):
        self.managers.add("grid")

    def bind(self, *args, **kwargs):
        pass

    def configure(self, **kwargs):
        self.configurations.append(kwargs)

    def columnconfigure(self, *args, **kwargs):
        pass

    def create_window(self, *args, **kwargs):
        pass

    def bbox(self, *args, **kwargs):
        return (0, 0, 100, 100)

    def yview(self, *args, **kwargs):
        pass

    def yview_scroll(self, *args, **kwargs):
        pass

    def heading(self, *args, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def get_children(self):
        return list(self.rows)

    def delete(self, item):
        self.rows.remove(item)

    def insert(self, parent, index, iid=None, values=()):
        self.rows.append(iid or str(len(self.rows)))

    def set(self, value):
        pass


class FakeVariable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeStyle:
    def theme_use(self, theme):
        pass

    def configure(self, *args, **kwargs):
        pass


def test_inicializa_interface_e_nao_mistura_gerenciadores_no_mesmo_pai():
    root = FakeWidget()
    root.title = lambda value: None
    root.geometry = lambda value: None
    root.minsize = lambda *values: None
    root.bind_all = lambda *args, **kwargs: None

    with patch.object(app.tk, "Canvas", FakeWidget), \
         patch.object(app.tk, "StringVar", FakeVariable), \
         patch.object(app.ttk, "Style", FakeStyle), \
         patch.object(app.ttk, "Frame", FakeWidget), \
         patch.object(app.ttk, "LabelFrame", FakeWidget), \
         patch.object(app.ttk, "Label", FakeWidget), \
         patch.object(app.ttk, "Entry", FakeWidget), \
         patch.object(app.ttk, "Combobox", FakeWidget), \
         patch.object(app.ttk, "Button", FakeWidget), \
         patch.object(app.ttk, "Treeview", FakeWidget), \
         patch.object(app.ttk, "Scrollbar", FakeWidget):
        simulador = app.Simulador(root)

    assert simulador.carteira
    assert simulador.tabela_carteira is not None
    assert simulador.tabela_evolucao is not None
    assert any(
        config.get("yscrollcommand") is not None
        for config in simulador.tabela_evolucao.configurations
    )
    assert simulador.resumo.get() == "Informe os dados e clique em calcular."

    def verificar_gerenciadores(widget):
        assert len(widget.managers) <= 1
        for child in widget.children:
            verificar_gerenciadores(child)

    verificar_gerenciadores(root)
