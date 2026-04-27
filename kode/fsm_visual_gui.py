import tkinter as tk
from tkinter import ttk
import math


STATES = ("S", "A", "B", "C")
START_STATE = "S"
ACCEPT_STATES = {"B"}
ALPHABET = {"0", "1"}

TRANSITIONS = {
    "S": {"0": "A", "1": "B"},
    "A": {"0": "C", "1": "B"},
    "B": {"0": "A", "1": "B"},
    "C": {"0": "C", "1": "C"},
}

STATE_DESCRIPTION = {
    "S": "Start state (belum membaca karakter).",
    "A": "Karakter terakhir 0, belum kena substring 00.",
    "B": "Karakter terakhir 1 (accept state).",
    "C": "Trap/dead state (sudah menemukan 00).",
}


def simulate_path(input_string: str):
    """
    Simulasi FSM dan mengembalikan data lintasan untuk visualisasi.
    """
    if not input_string:
        return {
            "ok": False,
            "error": "String kosong tidak diperbolehkan karena bahasa memakai (0+1)+.",
            "steps": [],
            "state_trace": [START_STATE],
            "accepted": False,
            "final_state": START_STATE,
        }

    current = START_STATE
    steps = []
    state_trace = [START_STATE]

    for idx, ch in enumerate(input_string, start=1):
        if ch not in ALPHABET:
            return {
                "ok": False,
                "error": f"Karakter ke-{idx} = '{ch}' tidak valid. Gunakan hanya 0 atau 1.",
                "steps": steps,
                "state_trace": state_trace,
                "accepted": False,
                "final_state": current,
            }

        nxt = TRANSITIONS[current][ch]
        steps.append(
            {
                "index": idx,
                "char": ch,
                "from_state": current,
                "to_state": nxt,
                "text": f"Step {idx}: baca '{ch}' : {current} -> {nxt}",
            }
        )
        current = nxt
        state_trace.append(current)

    accepted = current in ACCEPT_STATES
    return {
        "ok": True,
        "error": "",
        "steps": steps,
        "state_trace": state_trace,
        "accepted": accepted,
        "final_state": current,
    }


class FSMVisualizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FSM Visualizer - Praktikum Otomata")
        self.geometry("1120x700")
        self.minsize(1000, 640)

        self.sim_result = None
        self.current_step_pointer = 0  # index di state_trace
        self.is_playing = False
        self.play_after_id = None

        self.node_items = {}
        self.edge_items = {}
        self.last_highlighted_edge = None
        self.graph_positions = {}
        self.graph_radius = 38

        self._build_ui()
        self._draw_fsm_graph()
        self._render_step_state()

    def _build_ui(self):
        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(1, weight=1)

        title = ttk.Label(
            container,
            text="FSM Visualizer — L = { x in (0+1)+ | x berakhir 1 dan tidak punya substring 00 }",
            font=("Segoe UI", 13, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        graph_card = ttk.LabelFrame(container, text="Visualisasi Diagram FSM", padding=10)
        graph_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        graph_card.rowconfigure(0, weight=1)
        graph_card.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(graph_card, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        right = ttk.Frame(container)
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        input_card = ttk.LabelFrame(right, text="Input String", padding=10)
        input_card.grid(row=0, column=0, sticky="ew")
        input_card.columnconfigure(1, weight=1)

        ttk.Label(input_card, text="String biner:").grid(row=0, column=0, sticky="w")
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_card, textvariable=self.input_var, width=32)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.input_entry.focus()

        button_bar = ttk.Frame(input_card)
        button_bar.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Button(button_bar, text="Simulasikan", command=self.start_simulation).pack(side="left")
        ttk.Button(button_bar, text="Reset", command=self.reset_simulation).pack(side="left", padx=(8, 0))
        ttk.Button(button_bar, text="Contoh 110101", command=lambda: self._fill_example("110101")).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(button_bar, text="Contoh 1001", command=lambda: self._fill_example("1001")).pack(
            side="left", padx=(8, 0)
        )

        control_card = ttk.LabelFrame(right, text="Kontrol Animasi", padding=10)
        control_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        self.play_btn = ttk.Button(control_card, text="Play", command=self.toggle_play, state="disabled")
        self.play_btn.pack(side="left")
        self.prev_btn = ttk.Button(control_card, text="Prev", command=self.step_prev, state="disabled")
        self.prev_btn.pack(side="left", padx=(8, 0))
        self.next_btn = ttk.Button(control_card, text="Next", command=self.step_next, state="disabled")
        self.next_btn.pack(side="left", padx=(8, 0))

        self.speed_var = tk.IntVar(value=700)
        ttk.Label(control_card, text="Kecepatan (ms):").pack(side="left", padx=(14, 5))
        speed_scale = ttk.Scale(
            control_card,
            from_=250,
            to=1500,
            variable=self.speed_var,
            orient="horizontal",
            length=130,
        )
        speed_scale.pack(side="left")

        self.result_var = tk.StringVar(value="Hasil: -")
        self.result_badge = tk.Label(
            right,
            textvariable=self.result_var,
            bg="#e5e7eb",
            fg="#111827",
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=6,
        )
        self.result_badge.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.status_var = tk.StringVar(value="Status: menunggu input.")
        status_card = ttk.LabelFrame(right, text="Status", padding=10)
        status_card.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(status_card, textvariable=self.status_var, wraplength=380).pack(anchor="w")

        trace_card = ttk.LabelFrame(right, text="Jejak Transisi", padding=10)
        trace_card.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        trace_card.rowconfigure(0, weight=1)
        trace_card.columnconfigure(0, weight=1)

        self.trace_list = tk.Listbox(trace_card, font=("Consolas", 10), activestyle="none")
        self.trace_list.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(trace_card, orient="vertical", command=self.trace_list.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.trace_list.configure(yscrollcommand=scroll.set)

        legend_card = ttk.LabelFrame(right, text="Keterangan State", padding=10)
        legend_card.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        for name in STATES:
            marker = " (accept)" if name in ACCEPT_STATES else ""
            ttk.Label(legend_card, text=f"{name}{marker}: {STATE_DESCRIPTION[name]}").pack(anchor="w")

        self.bind("<Return>", lambda _e: self.start_simulation())

    def _draw_fsm_graph(self):
        c = self.canvas
        c.delete("all")

        # Posisi node di canvas.
        pos = {
            "S": (120, 220),
            "A": (340, 130),
            "B": (340, 320),
            "C": (560, 130),
        }
        radius = self.graph_radius
        self.graph_positions = pos

        # panah start ke S
        c.create_line(
            30,
            220,
            82,
            220,
            width=2,
            arrow=tk.LAST,
            arrowshape=(14, 16, 6),
            fill="#374151",
        )
        c.create_text(30, 195, text="start", font=("Segoe UI", 10), anchor="w", fill="#4b5563")

        # Edge utama
        self._draw_edge("S", "A", "0", curved=True, curve_sign=-1)
        self._draw_edge("S", "B", "1", curved=True, curve_sign=1)
        self._draw_edge("A", "B", "1", curved=True, curve_sign=-1)
        self._draw_edge("B", "A", "0", curved=True, curve_sign=1)
        self._draw_edge("A", "C", "0")

        # Loop pada B dan C
        self._draw_loop("B", "1", loop_side="bottom")
        self._draw_loop("C", "0,1", loop_side="right")

        for state, (x, y) in pos.items():
            circle = c.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                width=2,
                outline="#111827",
                fill="#f9fafb",
            )
            if state in ACCEPT_STATES:
                c.create_oval(
                    x - radius + 7,
                    y - radius + 7,
                    x + radius - 7,
                    y + radius - 7,
                    width=2,
                    outline="#111827",
                )
            label = c.create_text(x, y, text=state, font=("Segoe UI", 14, "bold"))
            self.node_items[state] = (circle, label)

    def _draw_edge(self, src, dst, label, curved=False, curve_sign=1):
        x1, y1 = self.graph_positions[src]
        x2, y2 = self.graph_positions[dst]
        radius = self.graph_radius

        # Potong titik awal/akhir agar panah berhenti di tepi lingkaran state.
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        ux = dx / dist
        uy = dy / dist
        sx = x1 + ux * radius
        sy = y1 + uy * radius
        ex = x2 - ux * radius
        ey = y2 - uy * radius

        if curved:
            # Normal vector untuk memisahkan jalur dua arah agar panah tidak tumpang tindih.
            nx = -uy
            ny = ux
            bend = 42 if src in ("A", "B") and dst in ("A", "B") else 36
            ctrl_x = (sx + ex) / 2 + nx * bend * curve_sign
            ctrl_y = (sy + ey) / 2 + ny * bend * curve_sign
            line = self.canvas.create_line(
                sx,
                sy,
                ctrl_x,
                ctrl_y,
                ex,
                ey,
                smooth=True,
                width=2,
                arrow=tk.LAST,
                arrowshape=(14, 16, 6),
                fill="#6b7280",
            )
            text_x = ctrl_x
            text_y = ctrl_y + (11 if curve_sign < 0 else -11)
        else:
            line = self.canvas.create_line(
                sx, sy, ex, ey, width=2, arrow=tk.LAST, arrowshape=(14, 16, 6), fill="#6b7280"
            )
            text_x = (sx + ex) / 2
            text_y = (sy + ey) / 2 - 12

        text = self.canvas.create_text(text_x, text_y, text=label, font=("Segoe UI", 10), fill="#374151")
        self.edge_items[(src, dst)] = (line, text)

    def _draw_loop(self, state, label, loop_side="right"):
        x, y = self.graph_positions[state]

        if loop_side == "right":
            points = (x + 38, y - 20, x + 95, y - 20, x + 95, y + 20, x + 38, y + 20)
            text_pos = (x + 100, y - 32)
        else:
            points = (x - 18, y + 38, x - 18, y + 85, x + 18, y + 85, x + 18, y + 38)
            text_pos = (x + 55, y + 78)

        line = self.canvas.create_line(
            *points, smooth=True, width=2, arrow=tk.LAST, arrowshape=(14, 16, 6), fill="#6b7280"
        )
        text = self.canvas.create_text(*text_pos, text=label, font=("Segoe UI", 10), fill="#374151")
        self.edge_items[(state, state)] = (line, text)

    def _fill_example(self, value):
        self.input_var.set(value)
        self.start_simulation()

    def start_simulation(self):
        self.stop_playback()
        raw = self.input_var.get().strip()
        self.sim_result = simulate_path(raw)
        self.current_step_pointer = 0
        self._refresh_trace_panel()
        self._refresh_buttons()
        self._render_step_state()
        # Auto-play agar visualisasi tidak terkesan stagnan.
        if self.sim_result.get("ok") and self.sim_result["steps"]:
            self.toggle_play()

    def reset_simulation(self):
        self.stop_playback()
        self.input_var.set("")
        self.sim_result = None
        self.current_step_pointer = 0
        self.trace_list.delete(0, tk.END)
        self.result_var.set("Hasil: -")
        self._style_result_badge("idle")
        self.status_var.set("Status: menunggu input.")
        self._refresh_buttons()
        self._render_step_state()
        self.input_entry.focus()

    def _refresh_trace_panel(self):
        self.trace_list.delete(0, tk.END)
        if not self.sim_result:
            return
        if not self.sim_result["ok"]:
            self.trace_list.insert(tk.END, f"ERROR: {self.sim_result['error']}")
            return
        self.trace_list.insert(tk.END, f"Start di state {START_STATE}")
        for step in self.sim_result["steps"]:
            self.trace_list.insert(tk.END, step["text"])

    def _refresh_buttons(self):
        has_steps = bool(self.sim_result and self.sim_result.get("ok") and self.sim_result["steps"])
        self.play_btn.configure(state=("normal" if has_steps else "disabled"))
        self.prev_btn.configure(state=("normal" if has_steps else "disabled"))
        self.next_btn.configure(state=("normal" if has_steps else "disabled"))
        self.play_btn.configure(text="Pause" if self.is_playing else "Play")

    def _render_step_state(self):
        self._highlight_state(START_STATE)
        self._clear_edge_highlight()
        self._style_result_badge("idle")

        if not self.sim_result:
            return

        if not self.sim_result["ok"]:
            self.result_var.set("Hasil: INPUT TIDAK VALID")
            self._style_result_badge("reject")
            self.status_var.set(f"Status: input tidak valid. {self.sim_result['error']}")
            return

        trace = self.sim_result["state_trace"]
        pointer = max(0, min(self.current_step_pointer, len(trace) - 1))
        current_state = trace[pointer]
        self._highlight_state(current_state)

        if pointer > 0:
            step = self.sim_result["steps"][pointer - 1]
            self._highlight_edge(step["from_state"], step["to_state"])
            self.status_var.set(
                f"Step {pointer}/{len(self.sim_result['steps'])}: baca '{step['char']}' -> state {step['to_state']}"
            )
        else:
            self.result_var.set("Hasil: sedang diproses...")
            self._style_result_badge("idle")
            self.status_var.set(f"Step 0/{len(self.sim_result['steps'])}: di start state S.")

        self.trace_list.selection_clear(0, tk.END)
        self.trace_list.activate(pointer)
        if pointer < self.trace_list.size():
            self.trace_list.selection_set(pointer)
            self.trace_list.see(pointer)

        if pointer == len(self.sim_result["steps"]):
            accepted = self.sim_result["accepted"]
            final_state = self.sim_result["final_state"]
            verdict = "DITERIMA" if accepted else "DITOLAK"
            reason = "akhir 1 dan tidak mengandung 00" if accepted else "akhir bukan 1 atau mengandung 00"
            self.result_var.set(f"Hasil: {verdict} (final state: {final_state})")
            self._style_result_badge("accept" if accepted else "reject")
            self._highlight_final_state(current_state=final_state, accepted=accepted)
            self.status_var.set(f"Hasil akhir: {verdict} (state {final_state}) - {reason}.")

    def _style_result_badge(self, mode):
        if mode == "accept":
            self.result_badge.configure(bg="#dcfce7", fg="#166534")
        elif mode == "reject":
            self.result_badge.configure(bg="#fee2e2", fg="#991b1b")
        else:
            self.result_badge.configure(bg="#e5e7eb", fg="#111827")

    def _highlight_final_state(self, current_state, accepted):
        circle, label = self.node_items[current_state]
        if accepted:
            self.canvas.itemconfig(circle, fill="#bbf7d0", outline="#15803d", width=3)
            self.canvas.itemconfig(label, fill="#166534")
        else:
            self.canvas.itemconfig(circle, fill="#fecaca", outline="#b91c1c", width=3)
            self.canvas.itemconfig(label, fill="#991b1b")

    def _highlight_state(self, active_state):
        for state, (circle, label) in self.node_items.items():
            if state == active_state:
                self.canvas.itemconfig(circle, fill="#dbeafe", outline="#2563eb", width=3)
                self.canvas.itemconfig(label, fill="#1d4ed8")
            else:
                self.canvas.itemconfig(circle, fill="#f9fafb", outline="#111827", width=2)
                self.canvas.itemconfig(label, fill="#111827")

    def _highlight_edge(self, src, dst):
        self._clear_edge_highlight()
        item = self.edge_items.get((src, dst))
        if not item:
            return
        line, text = item
        self.canvas.itemconfig(line, fill="#ef4444", width=3)
        self.canvas.itemconfig(text, fill="#b91c1c")
        self.last_highlighted_edge = (src, dst)

    def _clear_edge_highlight(self):
        if not self.last_highlighted_edge:
            return
        line, text = self.edge_items[self.last_highlighted_edge]
        self.canvas.itemconfig(line, fill="#6b7280", width=2)
        self.canvas.itemconfig(text, fill="#374151")
        self.last_highlighted_edge = None

    def step_next(self):
        if not self.sim_result or not self.sim_result.get("ok"):
            return
        max_pointer = len(self.sim_result["steps"])
        if self.current_step_pointer < max_pointer:
            self.current_step_pointer += 1
            self._render_step_state()
        else:
            self.stop_playback()

    def step_prev(self):
        if not self.sim_result or not self.sim_result.get("ok"):
            return
        if self.current_step_pointer > 0:
            self.current_step_pointer -= 1
            self._render_step_state()

    def toggle_play(self):
        if self.is_playing:
            self.stop_playback()
            return
        if not self.sim_result or not self.sim_result.get("ok"):
            return
        self.is_playing = True
        self._refresh_buttons()
        self._play_tick()

    def _play_tick(self):
        if not self.is_playing:
            return
        max_pointer = len(self.sim_result["steps"])
        if self.current_step_pointer >= max_pointer:
            self.stop_playback()
            return
        self.step_next()
        delay = int(self.speed_var.get())
        self.play_after_id = self.after(delay, self._play_tick)

    def stop_playback(self):
        self.is_playing = False
        if self.play_after_id is not None:
            self.after_cancel(self.play_after_id)
            self.play_after_id = None
        self._refresh_buttons()


if __name__ == "__main__":
    app = FSMVisualizerApp()
    app.mainloop()
