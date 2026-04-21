import customtkinter as ctk
from backend import VaultManager
from ui import LoginView, ListingsView, FormView, GeneratorView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AppController(ctk.CTk):
    """Enruta y coordina la lógica de la bóveda con las vistas visuales."""

    def __init__(self):
        super().__init__()
        self.title("PassManager Pro")
        self.geometry("1100x700")
        self.resizable(False, True)
        self.minsize(1100, 600)

        # Instancia única del backend (Datos y Seguridad)
        self.vault = VaultManager()

        # Contenedor principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.current_view = None
        self.show_login()

    def clear_container(self, container):
        for widget in container.winfo_children(): widget.destroy()

    # --- RUTAS PRINCIPALES ---
    def show_login(self):
        self.clear_container(self.main_container)
        # Inyecta el Vault y el Callback de éxito en la vista
        LoginView(self.main_container, self.vault, on_success=self.show_dashboard).pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_container(self.main_container)

        # Sidebar estático
        sidebar = ctk.CTkFrame(self.main_container, width=220, corner_radius=0, fg_color=("gray90", "gray13"))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="PassManager", font=("Segoe UI", 20, "bold")).pack(pady=(40, 40))

        # Área de contenido dinámico
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        # Navegación
        self.nav_btns = []

        def nav(btn, view_func):
            for b in self.nav_btns: b.configure(fg_color="transparent")
            btn.configure(fg_color=("gray80", "gray25"))
            view_func()

        def create_btn(text, func):
            btn = ctk.CTkButton(sidebar, text=text, fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                height=40, hover_color=("gray80", "gray25"))
            btn.configure(command=lambda b=btn: nav(b, func))
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_btns.append(btn)
            return btn

        btn_list = create_btn("Bóveda de Claves", self.nav_to_list)
        create_btn("Agregar Credencial", lambda: self.nav_to_form(None))
        create_btn("Generador Seguro", self.nav_to_generator)
        ctk.CTkButton(sidebar, text="Cerrar Sesión", fg_color="transparent", border_width=1, border_color="#E74C3C",
                      text_color="#E74C3C", command=self.show_login).pack(side="bottom", pady=30, padx=20, fill="x")

        # Iniciar en la lista
        nav(btn_list, self.nav_to_list)

    # --- SUB-RUTAS (CARGAN EN CONTENT_AREA) ---
    def nav_to_list(self):
        self.clear_container(self.content_area)
        ListingsView(self.content_area, self.vault, navigate_to_form=self.nav_to_form).pack(fill="both", expand=True)

    def nav_to_form(self, record=None):
        self.clear_container(self.content_area)
        # Si se navega atrás, vuelve a enrutar a la lista
        FormView(self.content_area, self.vault, record, navigate_back=lambda: self.nav_btns[0].invoke()).pack(
            fill="both", expand=True)

    def nav_to_generator(self):
        self.clear_container(self.content_area)
        GeneratorView(self.content_area, self.vault).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = AppController()
    app.mainloop()
