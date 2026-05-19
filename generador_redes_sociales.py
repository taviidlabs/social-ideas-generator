"""
Generador de Ideas para Redes Sociales
Usa Ollama (IA local y gratuita) para generar 30 ideas de publicaciones.

Requisitos:
    1. Tener Ollama instalado y corriendo: https://ollama.com
    2. Haber descargado un modelo: ollama pull llama3.2
    3. pip install ollama

Uso:
    python generador_redes_sociales.py
"""

import tkinter as tk
from tkinter import messagebox
import threading
import re
import math

try:
    import ollama
    OLLAMA_DISPONIBLE = True
except ImportError:
    OLLAMA_DISPONIBLE = False

# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────
MODEL = "llama3.2"

# Paleta de colores
BG_DARK      = "#0D0D0D"
BG_CARD      = "#161616"
BG_INPUT     = "#1E1E1E"
BG_HOVER     = "#252525"
ACCENT       = "#C8F135"   # verde lima vibrante
ACCENT_DARK  = "#A8D120"
TEXT_PRIMARY = "#F0F0F0"
TEXT_MUTED   = "#666666"
TEXT_DIM     = "#3A3A3A"
BORDER       = "#2A2A2A"
SUCCESS      = "#4ADE80"
WARNING      = "#FACC15"
ERROR_COLOR  = "#F87171"

# Categorías con colores
CATEGORIAS = [
    ("Educativo",       "#60A5FA"),
    ("Promocion",       ACCENT),
    ("Humor",           "#F472B6"),
    ("Comunidad",       "#A78BFA"),
    ("Behind scenes",   "#FB923C"),
    ("Testimonio",      "#34D399"),
]


# ──────────────────────────────────────────────
# LÓGICA
# ──────────────────────────────────────────────
def generar_ideas(negocio: str, producto: str) -> list[str]:
    prompt = f"""Eres un experto en marketing digital y redes sociales.
Genera exactamente 30 ideas creativas de publicaciones para redes sociales para:

- Nombre del negocio: {negocio}
- Tipo de producto/servicio: {producto}

Formato OBLIGATORIO:
- Numera del 1 al 30, una por linea.
- Variedad: tips, promociones, humor, preguntas, sorteos, fechas especiales, behind the scenes.
- Ideas concretas, listas para publicar, en español.
- SOLO las 30 ideas numeradas, sin introduccion ni texto extra.

1. [idea]
2. [idea]
...
30. [idea]"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = response["message"]["content"].strip()
    ideas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if re.match(r"^\d{1,2}\.", linea):
            idea = re.sub(r"^\d{1,2}\.\s*", "", linea).strip()
            if idea:
                ideas.append(idea)
    if len(ideas) < 10:
        ideas = [l.strip() for l in texto.splitlines() if l.strip()]
    return ideas[:30]


def verificar_ollama() -> tuple[bool, str]:
    try:
        modelos = ollama.list()
        nombres = [m.model for m in modelos.models]
        if not any(MODEL in n for n in nombres):
            disponibles = ", ".join(nombres) if nombres else "ninguno"
            return False, f"Modelo '{MODEL}' no encontrado.\nInstalados: {disponibles}\n\nEjecuta: ollama pull {MODEL}"
        return True, ""
    except Exception:
        return False, "Ollama no esta corriendo.\n\nAbre la app Ollama o ejecuta: ollama serve"


# ──────────────────────────────────────────────
# WIDGETS PERSONALIZADOS
# ──────────────────────────────────────────────
class RoundedEntry(tk.Canvas):
    """Entry con esquinas redondeadas y estilo dark."""
    def __init__(self, parent, placeholder="", width=300, **kwargs):
        super().__init__(parent, width=width, height=44,
                         bg=BG_DARK, highlightthickness=0, bd=0)
        self.placeholder = placeholder
        self._has_focus = False
        self._is_placeholder = True

        # Fondo redondeado
        self._draw_bg(BORDER)

        # Entry real encima
        self.entry = tk.Entry(self, bg=BG_INPUT, fg=TEXT_MUTED,
                              insertbackground=ACCENT,
                              relief="flat", bd=0,
                              font=("Consolas", 11),
                              highlightthickness=0)
        self.entry.insert(0, placeholder)
        self.create_window(width // 2, 22, window=self.entry, width=width - 32, height=28)

        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _draw_bg(self, border_color):
        self.delete("bg")
        w, h, r = int(self["width"]), 44, 8
        self.create_round_rect(2, 2, w-2, h-2, r, fill=BG_INPUT, outline=border_color, width=1, tags="bg")

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r,
               x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kwargs)

    def _on_focus_in(self, e):
        self._draw_bg(ACCENT)
        if self._is_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=TEXT_PRIMARY)
            self._is_placeholder = False

    def _on_focus_out(self, e):
        self._draw_bg(BORDER)
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=TEXT_MUTED)
            self._is_placeholder = True

    def get(self):
        v = self.entry.get()
        return "" if self._is_placeholder else v.strip()


class AnimatedButton(tk.Canvas):
    """Botón con fondo de color sólido y hover animado."""
    def __init__(self, parent, text, command, width=200, accent=True, **kwargs):
        h = 48
        super().__init__(parent, width=width, height=h,
                         bg=BG_DARK, highlightthickness=0, bd=0)
        self.command = command
        self.text = text
        self.width = width
        self.height = h
        self.accent = accent
        self._pressed = False

        self._draw(hover=False)
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, hover=False):
        self.delete("all")
        w, h, r = self.width, self.height, 10
        fill = ACCENT_DARK if hover else ACCENT
        if not self.accent:
            fill = BG_HOVER if hover else BG_CARD
        self.create_round_rect(0, 0, w, h, r, fill=fill, outline="")
        color = BG_DARK if self.accent else TEXT_PRIMARY
        self.create_text(w//2, h//2, text=self.text, fill=color,
                         font=("Consolas", 11, "bold"))

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r,
               x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kwargs)

    def _on_enter(self, e): self._draw(hover=True)
    def _on_leave(self, e): self._draw(hover=False)
    def _on_press(self, e): self._pressed = True
    def _on_release(self, e):
        if self._pressed:
            self._pressed = False
            if self.command:
                self.command()

    def set_state(self, state):
        if state == "disabled":
            self.unbind("<Button-1>")
            self.unbind("<ButtonRelease-1>")
            self.delete("all")
            w, h, r = self.width, self.height, 10
            self.create_round_rect(0, 0, w, h, r, fill=TEXT_DIM, outline="")
            self.create_text(w//2, h//2, text=self.text, fill=TEXT_MUTED,
                             font=("Consolas", 11, "bold"))
        else:
            self.bind("<Button-1>", self._on_press)
            self.bind("<ButtonRelease-1>", self._on_release)
            self._draw(hover=False)


class IdeaCard(tk.Frame):
    """Tarjeta individual de idea con número, texto y botón copiar."""
    def __init__(self, parent, numero, texto, categoria, on_copy, **kwargs):
        super().__init__(parent, bg=BG_CARD, pady=0, **kwargs)
        self.texto = texto
        self.on_copy = on_copy
        self._copied = False

        cat_nombre, cat_color = categoria

        # Contenedor interno con padding
        inner = tk.Frame(self, bg=BG_CARD, padx=14, pady=10)
        inner.pack(fill="x", expand=True)

        # Fila superior: número + badge categoría
        top = tk.Frame(inner, bg=BG_CARD)
        top.pack(fill="x")

        tk.Label(top, text=f"{numero:02d}", bg=BG_CARD,
                 fg=ACCENT, font=("Consolas", 10, "bold")).pack(side="left")

        tk.Label(top, text=f"  {cat_nombre}", bg=BG_CARD,
                 fg=cat_color, font=("Consolas", 8)).pack(side="left", padx=8)

        # Botón copiar a la derecha
        self.btn_copy = tk.Label(top, text="copiar", bg=BG_CARD,
                                  fg=TEXT_MUTED, font=("Consolas", 8),
                                  cursor="hand2")
        self.btn_copy.pack(side="right")
        self.btn_copy.bind("<Button-1>", self._copy)
        self.btn_copy.bind("<Enter>", lambda e: self.btn_copy.config(fg=ACCENT))
        self.btn_copy.bind("<Leave>", lambda e: self.btn_copy.config(
            fg=SUCCESS if self._copied else TEXT_MUTED))

        # Texto de la idea
        tk.Label(inner, text=texto, bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10), wraplength=560,
                 justify="left", anchor="w").pack(fill="x", pady=(4, 0))

        # Línea separadora inferior
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

        # Hover effect
        self.bind("<Enter>", self._hover_in)
        self.bind("<Leave>", self._hover_out)
        inner.bind("<Enter>", self._hover_in)
        inner.bind("<Leave>", self._hover_out)

    def _hover_in(self, e):
        self.config(bg=BG_HOVER)
        for w in self.winfo_children():
            try: w.config(bg=BG_HOVER)
            except: pass

    def _hover_out(self, e):
        self.config(bg=BG_CARD)
        for w in self.winfo_children():
            try: w.config(bg=BG_CARD)
            except: pass

    def _copy(self, e):
        self._copied = True
        self.clipboard_clear()
        self.clipboard_append(self.texto)
        self.btn_copy.config(text="✓ copiado", fg=SUCCESS)
        self.after(2000, self._reset_copy)
        if self.on_copy:
            self.on_copy(self.texto)

    def _reset_copy(self):
        self._copied = False
        self.btn_copy.config(text="copiar", fg=TEXT_MUTED)


# ──────────────────────────────────────────────
# APP PRINCIPAL
# ──────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Ideas — Powered by Ollama")
        self.geometry("720x800")
        self.minsize(640, 600)
        self.configure(bg=BG_DARK)
        self.ideas: list[str] = []
        self._anim_angle = 0
        self._anim_id = None
        self._build_ui()
        if not OLLAMA_DISPONIBLE:
            self.after(400, self._error_libreria)
        else:
            self.after(400, self._verificar_inicio)

    # ── UI ────────────────────────────────────
    def _build_ui(self):

        # ── HEADER ────────────────────────────
        header = tk.Frame(self, bg=BG_DARK, pady=28, padx=32)
        header.pack(fill="x")

        # Logo / título
        title_row = tk.Frame(header, bg=BG_DARK)
        title_row.pack(anchor="w")

        tk.Label(title_row, text="◈", bg=BG_DARK, fg=ACCENT,
                 font=("Consolas", 22)).pack(side="left", padx=(0, 10))

        title_col = tk.Frame(title_row, bg=BG_DARK)
        title_col.pack(side="left")

        tk.Label(title_col, text="SOCIAL IDEAS", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Consolas", 18, "bold")).pack(anchor="w")
        tk.Label(title_col, text="generador de contenido para redes sociales",
                 bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Consolas", 9)).pack(anchor="w")

        # Badge estado Ollama
        self.lbl_status = tk.Label(header, text="● verificando...",
                                   bg=BG_DARK, fg=TEXT_MUTED,
                                   font=("Consolas", 8))
        self.lbl_status.pack(anchor="e", pady=(4, 0))

        # Línea decorativa
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x")

        # ── FORMULARIO ────────────────────────
        form_outer = tk.Frame(self, bg=BG_DARK, padx=32, pady=24)
        form_outer.pack(fill="x")

        tk.Label(form_outer, text="CONFIGURA TU NEGOCIO",
                 bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Consolas", 8)).pack(anchor="w", pady=(0, 12))

        fields = tk.Frame(form_outer, bg=BG_DARK)
        fields.pack(fill="x")
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)

        # Campo negocio
        col1 = tk.Frame(fields, bg=BG_DARK)
        col1.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tk.Label(col1, text="nombre del negocio", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Consolas", 8)).pack(anchor="w", pady=(0, 6))
        self.entry_negocio = RoundedEntry(col1, placeholder="Panaderia Dona Rosa",
                                          width=290)
        self.entry_negocio.pack(fill="x")

        # Campo producto
        col2 = tk.Frame(fields, bg=BG_DARK)
        col2.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        tk.Label(col2, text="tipo de producto / servicio", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Consolas", 8)).pack(anchor="w", pady=(0, 6))
        self.entry_producto = RoundedEntry(col2, placeholder="Pan artesanal y reposteria",
                                           width=290)
        self.entry_producto.pack(fill="x")

        # ── BOTONES ───────────────────────────
        btn_row = tk.Frame(form_outer, bg=BG_DARK)
        btn_row.pack(fill="x", pady=(16, 0))

        self.btn_generar = AnimatedButton(btn_row,
                                          text="⚡  GENERAR 30 IDEAS",
                                          command=self._on_generar,
                                          width=320, accent=True)
        self.btn_generar.pack(side="left")

        self.btn_copiar_todo = AnimatedButton(btn_row,
                                              text="⎘  COPIAR TODO",
                                              command=self._copiar_todo,
                                              width=160, accent=False)
        self.btn_copiar_todo.pack(side="right")
        self.btn_copiar_todo.pack_forget()

        # ── STATUS BAR ────────────────────────
        status_bar = tk.Frame(self, bg=BG_CARD, padx=32, pady=10)
        status_bar.pack(fill="x")

        self.canvas_anim = tk.Canvas(status_bar, width=16, height=16,
                                     bg=BG_CARD, highlightthickness=0)
        self.canvas_anim.pack(side="left", padx=(0, 8))

        self.lbl_progreso = tk.Label(status_bar, text="listo para generar",
                                     bg=BG_CARD, fg=TEXT_MUTED,
                                     font=("Consolas", 9))
        self.lbl_progreso.pack(side="left")

        self.lbl_count = tk.Label(status_bar, text="",
                                  bg=BG_CARD, fg=ACCENT,
                                  font=("Consolas", 9, "bold"))
        self.lbl_count.pack(side="right")

        # ── AREA DE RESULTADOS ────────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        self.scroll_frame_outer = tk.Frame(self, bg=BG_DARK)
        self.scroll_frame_outer.pack(fill="both", expand=True)

        # Canvas scrollable
        self.canvas_scroll = tk.Canvas(self.scroll_frame_outer,
                                       bg=BG_DARK, highlightthickness=0,
                                       bd=0)
        self.scrollbar = tk.Scrollbar(self.scroll_frame_outer,
                                      orient="vertical",
                                      command=self.canvas_scroll.yview,
                                      bg=BG_CARD, troughcolor=BG_DARK,
                                      activebackground=ACCENT,
                                      width=6)
        self.canvas_scroll.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas_scroll, bg=BG_DARK)
        self.canvas_window = self.canvas_scroll.create_window(
            (0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas_scroll.bind("<Configure>", self._on_canvas_configure)

        # Enlazar scroll global: funciona sobre cualquier widget de la ventana
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux usa Button-4 / Button-5 en lugar de MouseWheel
        self.bind_all("<Button-4>", lambda e: self.canvas_scroll.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas_scroll.yview_scroll( 1, "units"))

        # Placeholder vacío
        self._mostrar_placeholder()

        # ── FOOTER ────────────────────────────
        footer = tk.Frame(self, bg="#0A0A0A", pady=8)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text="// © 2026 Deyvid Torrez · All rights reserved  ·  modelo: " + MODEL,
                 bg="#0A0A0A", fg=TEXT_MUTED,
                 font=("Consolas", 7)).pack()

    def _mostrar_placeholder(self):
        for w in self.inner_frame.winfo_children():
            w.destroy()
        ph = tk.Frame(self.inner_frame, bg=BG_DARK, pady=60)
        ph.pack(fill="x")
        tk.Label(ph, text="◈", bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 36)).pack()
        tk.Label(ph, text="ingresa tu negocio y genera ideas",
                 bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 10)).pack(pady=(8, 0))

    # ── Scroll ────────────────────────────────
    def _on_frame_configure(self, e):
        self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas_scroll.itemconfig(self.canvas_window, width=e.width)

    def _on_mousewheel(self, e):
        self.canvas_scroll.yview_scroll(int(-1*(e.delta/120)), "units")

    # ── Animación spinner ─────────────────────
    def _start_spinner(self):
        self._anim_angle = 0
        self._animate_spinner()

    def _animate_spinner(self):
        self.canvas_anim.delete("all")
        cx, cy, r = 8, 8, 5
        for i in range(8):
            angle = math.radians(self._anim_angle + i * 45)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            alpha = int(255 * (i + 1) / 8)
            color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
            self.canvas_anim.create_oval(x-1.5, y-1.5, x+1.5, y+1.5,
                                         fill=color, outline="")
        self._anim_angle = (self._anim_angle + 15) % 360
        self._anim_id = self.after(50, self._animate_spinner)

    def _stop_spinner(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self.canvas_anim.delete("all")
        self.canvas_anim.create_oval(3, 3, 13, 13, fill=SUCCESS, outline="")

    # ── Verificaciones ────────────────────────
    def _error_libreria(self):
        messagebox.showerror("Libreria no instalada",
                             "Ejecuta:  pip install ollama\nLuego reinicia el script.")
        self.btn_generar.set_state("disabled")

    def _verificar_inicio(self):
        ok, msg = verificar_ollama()
        if not ok:
            self.lbl_status.config(text="● offline", fg=ERROR_COLOR)
            messagebox.showwarning("Ollama no disponible", msg)
            self.btn_generar.set_state("disabled")
        else:
            self.lbl_status.config(text="● ollama online", fg=SUCCESS)

    # ── Generación ────────────────────────────
    def _on_generar(self):
        negocio  = self.entry_negocio.get()
        producto = self.entry_producto.get()

        if not negocio or not producto:
            messagebox.showwarning("Faltan datos",
                                   "Completa el nombre del negocio\ny el tipo de producto.")
            return

        self.btn_generar.set_state("disabled")
        self.btn_copiar_todo.pack_forget()
        self.lbl_count.config(text="")
        self.lbl_progreso.config(text="generando con ollama...  puede tardar unos segundos",
                                 fg=WARNING)
        self._start_spinner()
        self._mostrar_placeholder()

        threading.Thread(target=self._tarea, args=(negocio, producto), daemon=True).start()

    def _tarea(self, negocio, producto):
        try:
            ideas = generar_ideas(negocio, producto)
            self.after(0, self._mostrar_ideas, ideas)
        except Exception as exc:
            msg = str(exc)
            if "connection" in msg.lower() or "refused" in msg.lower():
                msg = "Ollama no esta corriendo.\n\nAbre la app Ollama o ejecuta: ollama serve"
            self.after(0, self._mostrar_error, msg)

    def _mostrar_ideas(self, ideas: list[str]):
        self.ideas = ideas
        self._stop_spinner()
        self.lbl_progreso.config(text="ideas generadas — haz clic para copiar", fg=SUCCESS)
        self.lbl_count.config(text=f"{len(ideas)} ideas")
        self.btn_copiar_todo.pack(side="right")
        self.btn_generar.set_state("normal")

        for w in self.inner_frame.winfo_children():
            w.destroy()

        # Título sección
        header = tk.Frame(self.inner_frame, bg=BG_DARK, padx=24, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="IDEAS GENERADAS", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Consolas", 8)).pack(anchor="w")

        # Tarjetas
        for i, idea in enumerate(ideas):
            cat = CATEGORIAS[i % len(CATEGORIAS)]
            card = IdeaCard(self.inner_frame, numero=i+1, texto=idea,
                            categoria=cat, on_copy=self._on_idea_copiada)
            card.pack(fill="x", padx=16, pady=(0, 2))

        # Padding final
        tk.Frame(self.inner_frame, bg=BG_DARK, height=20).pack()

        self.canvas_scroll.yview_moveto(0)

    def _mostrar_error(self, msg):
        self._stop_spinner()
        self.btn_generar.set_state("normal")
        self.lbl_progreso.config(text="error al generar", fg=ERROR_COLOR)
        messagebox.showerror("Error", msg)

    def _on_idea_copiada(self, texto):
        self.lbl_progreso.config(text="idea copiada al portapapeles ✓", fg=SUCCESS)
        self.after(3000, lambda: self.lbl_progreso.config(
            text="ideas generadas — haz clic para copiar", fg=SUCCESS))

    def _copiar_todo(self):
        if not self.ideas:
            return
        texto = "\n\n".join(f"{i+1}. {idea}" for i, idea in enumerate(self.ideas))
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.lbl_progreso.config(text=f"todas las {len(self.ideas)} ideas copiadas ✓", fg=SUCCESS)
        self.after(3000, lambda: self.lbl_progreso.config(
            text="ideas generadas — haz clic para copiar", fg=SUCCESS))


# ──────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
