import customtkinter as ctk
import pyperclip
from tkinter import messagebox

# Configuración visual compartida
FONT_H1 = ("Segoe UI", 28, "bold")
FONT_H2 = ("Segoe UI", 20, "bold")
FONT_BOLD = ("Segoe UI", 14, "bold")
FONT_REGULAR = ("Segoe UI", 14)
FONT_SMALL = ("Segoe UI", 12)
CARD_COLOR = ("gray90", "gray13")


class LoginView(ctk.CTkFrame):
    def __init__(self, master, vault, on_success):
        super().__init__(master, fg_color="transparent")
        self.vault = vault
        self.on_success = on_success

        card = ctk.CTkFrame(self, width=450, height=400, corner_radius=20, fg_color=CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="PassManager Pro", font=FONT_H1).pack(pady=(40, 10))
        ctk.CTkLabel(card, text="Acceso a la Bóveda de Seguridad", font=FONT_REGULAR, text_color="gray").pack(
            pady=(0, 30))

        pwd_frame = ctk.CTkFrame(card, fg_color="transparent")
        pwd_frame.pack(pady=10, padx=40, fill="x")

        self.pwd_entry = ctk.CTkEntry(pwd_frame, placeholder_text="Contraseña Maestra", show="*", height=45,
                                      font=FONT_REGULAR)
        self.pwd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.show_btn = ctk.CTkButton(pwd_frame, text="Ver", width=50, height=45, fg_color="transparent",
                                      border_width=1, command=self.toggle_pwd)
        self.show_btn.pack(side="right")

        ctk.CTkButton(card, text="Desbloquear / Registrar", height=45, font=FONT_BOLD, command=self.auth).pack(
            pady=(30, 20), padx=40, fill="x")

    def toggle_pwd(self):
        is_hidden = self.pwd_entry.cget("show") == "*"
        self.pwd_entry.configure(show="" if is_hidden else "*")
        self.show_btn.configure(text="Ocultar" if is_hidden else "Ver")

    def auth(self):
        pwd = self.pwd_entry.get()
        if pwd and self.vault.authenticate(pwd):
            self.on_success()
        elif pwd:
            messagebox.showerror("Error", "La contraseña maestra es incorrecta.")


class ListingsView(ctk.CTkFrame):
    def __init__(self, master, vault, navigate_to_form):
        super().__init__(master, fg_color="transparent")
        self.vault = vault
        self.navigate_to_form = navigate_to_form
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children(): widget.destroy()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Tus Credenciales", font=FONT_H1).pack(side="left")
        ctk.CTkLabel(header, text=f"Total: {len(self.vault.vault_data)}", font=FONT_REGULAR, text_color="gray").pack(
            side="right", pady=10)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not self.vault.vault_data:
            ctk.CTkLabel(scroll, text="Tu bóveda está vacía.", font=FONT_H2, text_color="gray").pack(pady=100)
            return

        for rec in self.vault.vault_data:
            decrypted = self.vault.decrypt(rec['password'])
            _, color, label_text = self.vault.check_strength(decrypted)

            card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=10)
            card.pack(fill="x", pady=6, padx=5)
            for i, weight in enumerate([2, 3, 1, 0]): card.columnconfigure(i, weight=weight)

            # Info
            info_sub = ctk.CTkFrame(card, fg_color="transparent")
            info_sub.grid(row=0, column=0, sticky="w", padx=15, pady=8)
            ctk.CTkLabel(info_sub, text=rec['site'], font=FONT_BOLD).pack(anchor="w")
            ctk.CTkLabel(info_sub, text=rec['username'], font=FONT_SMALL, text_color="gray").pack(anchor="w")

            # Contraseña
            pwd_sub = ctk.CTkFrame(card, fg_color="transparent")
            pwd_sub.grid(row=0, column=1, sticky="w", padx=10, pady=8)
            ctk.CTkLabel(pwd_sub, text="Contraseña", font=FONT_SMALL, text_color="gray").pack(anchor="w")
            pwd_row = ctk.CTkFrame(pwd_sub, fg_color="transparent")
            pwd_row.pack(fill="x")

            pwd_lbl = ctk.CTkLabel(pwd_row, text="••••••••••••", font=FONT_REGULAR)
            pwd_lbl.pack(side="left")
            toggle_btn = ctk.CTkButton(pwd_row, text="Mostrar", width=50, height=20, font=FONT_SMALL,
                                       fg_color="transparent", border_width=1, text_color="gray")
            toggle_btn.pack(side="left", padx=10)
            toggle_btn.configure(command=self.make_toggle(pwd_lbl, toggle_btn, decrypted))

            # Seguridad
            sec_sub = ctk.CTkFrame(card, fg_color="transparent")
            sec_sub.grid(row=0, column=2, sticky="w", padx=10, pady=8)
            ctk.CTkLabel(sec_sub, text="Seguridad", font=FONT_SMALL, text_color="gray").pack(anchor="w")
            ctk.CTkLabel(sec_sub, text=label_text, text_color=color, font=FONT_BOLD).pack(anchor="w")

            # Acciones
            act_sub = ctk.CTkFrame(card, fg_color="transparent")
            act_sub.grid(row=0, column=3, sticky="e", padx=15, pady=8)
            ctk.CTkButton(act_sub, text="Copiar", width=60, font=FONT_BOLD,
                          command=lambda p=decrypted: self.copy(p)).pack(side="left", padx=3)
            ctk.CTkButton(act_sub, text="Editar", width=60, fg_color="transparent", border_width=1,
                          command=lambda r=rec: self.navigate_to_form(r)).pack(side="left", padx=3)
            ctk.CTkButton(act_sub, text="Eliminar", width=60, fg_color="transparent", text_color="#E74C3C",
                          hover_color=("#ffcccc", "#4a1914"), command=lambda i=rec['id']: self.delete(i)).pack(
                side="left", padx=3)

    def make_toggle(self, lbl, btn, secret):
        def _toggle():
            if lbl.cget("text") == "••••••••••••":
                lbl.configure(text=secret);
                btn.configure(text="Ocultar")
            else:
                lbl.configure(text="••••••••••••");
                btn.configure(text="Mostrar")

        return _toggle

    def copy(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("Éxito", "Copiado al portapapeles")

    def delete(self, rid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
            self.vault.delete_record(rid)
            self.build_ui()


class FormView(ctk.CTkFrame):
    def __init__(self, master, vault, record, navigate_back):
        super().__init__(master, fg_color="transparent")
        self.vault = vault
        self.record = record
        self.navigate_back = navigate_back
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Editar Credencial" if self.record else "Nueva Credencial", font=FONT_H1).pack(
            anchor="w", pady=(0, 20))
        form = ctk.CTkFrame(self, corner_radius=15, fg_color=CARD_COLOR)
        form.pack(pady=10, fill="x", padx=5)

        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.pack(padx=40, pady=30, fill="x")

        ctk.CTkLabel(fields, text="Sitio Web", font=FONT_BOLD).pack(anchor="w")
        self.s_e = ctk.CTkEntry(fields, height=40, font=FONT_REGULAR)
        self.s_e.pack(fill="x", pady=(5, 20))

        ctk.CTkLabel(fields, text="Usuario/Email", font=FONT_BOLD).pack(anchor="w")
        self.u_e = ctk.CTkEntry(fields, height=40, font=FONT_REGULAR)
        self.u_e.pack(fill="x", pady=(5, 20))

        ctk.CTkLabel(fields, text="Contraseña", font=FONT_BOLD).pack(anchor="w")
        pwd_frame = ctk.CTkFrame(fields, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(5, 5))
        self.p_e = ctk.CTkEntry(pwd_frame, show="*", height=40, font=FONT_REGULAR)
        self.p_e.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.show_btn = ctk.CTkButton(pwd_frame, text="Ver", width=60, height=40, fg_color="transparent",
                                      border_width=1, command=self.toggle_pwd)
        self.show_btn.pack(side="right")

        meter = ctk.CTkFrame(fields, fg_color="transparent")
        meter.pack(fill="x", pady=(0, 20))
        self.bar = ctk.CTkProgressBar(meter, height=8)
        self.bar.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.bar.set(0)
        self.lbl_sec = ctk.CTkLabel(meter, text="Seguridad: -", font=FONT_SMALL, width=150, anchor="e")
        self.lbl_sec.pack(side="right")

        self.p_e.bind("<KeyRelease>", self.update_meter)

        if self.record:
            self.s_e.insert(0, self.record['site'])
            self.u_e.insert(0, self.record['username'])
            self.p_e.insert(0, self.vault.decrypt(self.record['password']))
            self.update_meter()

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.pack(padx=40, pady=(0, 30), fill="x")
        ctk.CTkButton(actions, text="Cancelar", fg_color="transparent", border_width=1, height=40, font=FONT_BOLD,
                      text_color="gray", command=self.navigate_back).pack(side="left", expand=True, fill="x",
                                                                          padx=(0, 10))
        ctk.CTkButton(actions, text="Guardar", height=40, font=FONT_BOLD, command=self.save).pack(side="right",
                                                                                                  expand=True, fill="x",
                                                                                                  padx=(10, 0))

    def toggle_pwd(self):
        is_hidden = self.p_e.cget("show") == "*"
        self.p_e.configure(show="" if is_hidden else "*")
        self.show_btn.configure(text="Ocultar" if is_hidden else "Ver")

    def update_meter(self, *args):
        p = self.p_e.get()
        if not p:
            self.bar.set(0);
            self.lbl_sec.configure(text="Seguridad: -", text_color="gray");
            return
        score, color, label = self.vault.check_strength(p)
        self.bar.set(score)
        self.bar.configure(progress_color=color)
        self.lbl_sec.configure(text=f"Seguridad: {label}", text_color=color)

    def save(self):
        s, u, p = self.s_e.get(), self.u_e.get(), self.p_e.get()
        if not all([s, u, p]):
            messagebox.showwarning("Incompleto", "Todos los campos son requeridos.");
            return

        if self.record:
            self.vault.update_record(self.record['id'], s, u, p)
        else:
            self.vault.add_record(s, u, p)
        self.navigate_back()


class GeneratorView(ctk.CTkFrame):
    def __init__(self, master, vault):
        super().__init__(master, fg_color="transparent")
        self.vault = vault
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Generador de Contraseñas", font=FONT_H1).pack(anchor="w", pady=(0, 20))
        gen_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=CARD_COLOR)
        gen_frame.pack(fill="x", padx=5)

        self.res = ctk.CTkEntry(gen_frame, font=("Consolas", 22, "bold"), justify="center", height=60)
        self.res.pack(fill="x", padx=40, pady=(40, 10))

        meter = ctk.CTkFrame(gen_frame, fg_color="transparent")
        meter.pack(fill="x", padx=40, pady=10)
        self.bar = ctk.CTkProgressBar(meter, height=10)
        self.bar.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.lbl_sec = ctk.CTkLabel(meter, text="Seguridad: -", font=FONT_BOLD, width=150, anchor="e")
        self.lbl_sec.pack(side="right")
        self.res.bind("<KeyRelease>", self.update_meter)

        ctrls = ctk.CTkFrame(gen_frame, fg_color="transparent")
        ctrls.pack(fill="x", padx=40, pady=10)

        self.mode = ctk.StringVar(value="Passphrase (Recomendado)")
        ctk.CTkSegmentedButton(ctrls, values=["Caracteres", "Passphrase (Recomendado)"], variable=self.mode,
                               command=self.mode_changed).pack(fill="x", pady=(0, 15))

        slider_f = ctk.CTkFrame(ctrls, fg_color="transparent")
        slider_f.pack(fill="x", pady=10)
        self.l_var = ctk.IntVar(value=16)
        ctk.CTkLabel(slider_f, text="Longitud:", font=FONT_BOLD).pack(side="left")
        self.lbl_len = ctk.CTkLabel(slider_f, text="16", font=FONT_BOLD, text_color="#1ABC9C", width=30)
        self.lbl_len.pack(side="left", padx=10)
        self.slider = ctk.CTkSlider(slider_f, variable=self.l_var,
                                    command=lambda v: self.lbl_len.configure(text=str(int(v))))
        self.slider.pack(side="right", fill="x", expand=True, padx=20)

        opts = ctk.CTkFrame(ctrls, fg_color="transparent")
        opts.pack(fill="x", pady=10)
        self.v_up, self.v_lo, self.v_nu, self.v_sy = (ctk.BooleanVar(value=True) for _ in range(4))
        self.switches = [
            ctk.CTkSwitch(opts, text="Mayúsculas", variable=self.v_up),
            ctk.CTkSwitch(opts, text="Minúsculas", variable=self.v_lo),
            ctk.CTkSwitch(opts, text="Números", variable=self.v_nu),
            ctk.CTkSwitch(opts, text="Símbolos", variable=self.v_sy)
        ]
        for sw in self.switches: sw.pack(side="left", expand=True)

        btns = ctk.CTkFrame(gen_frame, fg_color="transparent")
        btns.pack(pady=(10, 40))
        ctk.CTkButton(btns, text="Generar", height=45, font=FONT_BOLD, command=self.gen).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Copiar", height=45, font=FONT_BOLD, fg_color="transparent", border_width=2,
                      command=lambda: pyperclip.copy(self.res.get())).pack(side="left", padx=10)

        self.mode_changed()

    def update_meter(self, *args):
        p = self.res.get()
        if not p:
            self.bar.set(0);
            self.lbl_sec.configure(text="Seguridad: -", text_color="gray");
            return
        score, color, label = self.vault.check_strength(p)
        self.bar.set(score);
        self.bar.configure(progress_color=color)
        self.lbl_sec.configure(text=f"Seguridad: {label}", text_color=color)

    def mode_changed(self, *args):
        if self.mode.get() == "Caracteres":
            self.slider.configure(from_=8, to=32)
            if not (8 <= self.l_var.get() <= 32): self.l_var.set(16)
            for sw in self.switches: sw.configure(state="normal")
        else:
            self.slider.configure(from_=3, to=8)
            if self.l_var.get() > 8: self.l_var.set(4)
            for sw in self.switches: sw.configure(state="disabled")
        self.lbl_len.configure(text=str(int(self.l_var.get())))
        self.gen()

    def gen(self):
        pwd = self.vault.generate_password(
            self.mode.get(), self.l_var.get(),
            self.v_up.get(), self.v_lo.get(), self.v_nu.get(), self.v_sy.get()
        )
        if not pwd: messagebox.showwarning("Error", "Selecciona caracteres."); return
        self.res.delete(0, 'end');
        self.res.insert(0, pwd)
        self.update_meter()
