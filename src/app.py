from dataclasses import replace
from pathlib import Path
import sys
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, simpledialog, ttk

from discovery import default_save_root, discover_saves
from i18n import LANGUAGES, Translator
from models import Animal, Farmhand, SaveData, SavePaths
from reader import SaveConsistencyError, load_save
from version import APP_VERSION
from writer import SaveWriteError, save_changes


AUTHOR_URL = "https://github.com/fyihang"
REPOSITORY_URL = "https://github.com/fyihang/StardewValleyTool"
VERSION_URL = "https://github.com/fyihang/StardewValleyTool/releases/latest"


def open_url(url: str) -> None:
    webbrowser.open_new_tab(url)


def resource_dir() -> Path:
    """Return the i18n directory in source and PyInstaller environments."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root) / "i18n"
    return Path(__file__).parent.parent / "i18n"


class SaveManagerApp:
    def __init__(self, root: tk.Tk, save_root: Path | None = None) -> None:
        self.root = root
        self.save_root = save_root or default_save_root()
        self.translator = Translator(resource_dir())
        self.paths: tuple[SavePaths, ...] = ()
        self.loaded: SaveData | None = None
        self.selected: SavePaths | None = None
        self.vars = {key: tk.StringVar() for key in ("farmer", "farm", "favorite")}
        self.farmhand_vars = {key: tk.StringVar() for key in ("farmer", "favorite")}
        self._farmhands: list[Farmhand] = []
        self._active_farmhand: int | None = None
        self._build()
        self.refresh_saves()

    def _build(self) -> None:
        self.root.minsize(760, 480)
        outer = ttk.Frame(self.root, padding=12); outer.pack(fill="both", expand=True)
        toolbar = ttk.Frame(outer); toolbar.pack(fill="x")
        self.refresh_button = ttk.Button(toolbar, command=self.refresh_saves); self.refresh_button.pack(side="left")
        self.choose_root_button = ttk.Button(toolbar, command=self.choose_save_root); self.choose_root_button.pack(side="left", padx=(6, 0))
        ttk.Label(toolbar, textvariable=tk.StringVar(value="")).pack(side="left", padx=8)
        self.language = tk.StringVar(value=LANGUAGES[0][0])
        self.language_box = ttk.Combobox(toolbar, width=10, state="readonly", values=tuple(name for _, name in LANGUAGES))
        self.language_box.current(0); self.language_box.bind("<<ComboboxSelected>>", self._change_language); self.language_box.pack(side="right")
        self.language_label = ttk.Label(toolbar); self.language_label.pack(side="right", padx=6)
        panes = ttk.PanedWindow(outer, orient="horizontal"); panes.pack(fill="both", expand=True, pady=10)
        left = ttk.Frame(panes, padding=4); right = ttk.Frame(panes, padding=8); panes.add(left, weight=1); panes.add(right, weight=3)
        self.save_list = tk.Listbox(left, exportselection=False); self.save_list.pack(fill="both", expand=True); self.save_list.bind("<<ListboxSelect>>", self._select_save)
        self.status = tk.StringVar(); ttk.Label(left, textvariable=self.status, wraplength=180).pack(fill="x", pady=6)
        self.labels = {}
        for row, (key, variable) in enumerate(self.vars.items()):
            label = ttk.Label(right); label.grid(row=row, column=0, sticky="w", pady=4); self.labels[key] = label
            entry = ttk.Entry(right, textvariable=variable); entry.grid(row=row, column=1, sticky="ew", pady=4); variable.trace_add("write", lambda *_: self._update_save_state())
        right.columnconfigure(1, weight=1)
        self.animals_label = ttk.Label(right); self.animals_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 3))
        self.animals = ttk.Treeview(right, columns=("species", "name"), show="headings", height=7); self.animals.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.animals.column("species", width=180); self.animals.bind("<Double-1>", self._edit_animal)
        self.farmhands_frame = ttk.LabelFrame(right); self.farmhands_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 3))
        self.farmhands_label = ttk.Label(self.farmhands_frame); self.farmhands_label.grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.farmhand_box = ttk.Combobox(self.farmhands_frame, state="readonly"); self.farmhand_box.grid(row=0, column=1, sticky="ew", padx=4, pady=4); self.farmhand_box.bind("<<ComboboxSelected>>", self._select_farmhand)
        self.farmhand_labels = {}
        for row, (key, variable) in enumerate(self.farmhand_vars.items(), start=1):
            label = ttk.Label(self.farmhands_frame); label.grid(row=row, column=0, sticky="w", padx=4, pady=2); self.farmhand_labels[key] = label
            entry = ttk.Entry(self.farmhands_frame, textvariable=variable); entry.grid(row=row, column=1, sticky="ew", padx=4, pady=2); variable.trace_add("write", lambda *_: self._update_save_state())
        self.farmhands_frame.columnconfigure(1, weight=1)
        right.rowconfigure(4, weight=1)
        footer = ttk.Frame(outer); footer.pack(fill="x")
        self.about_button = ttk.Button(footer, command=self.show_about); self.about_button.pack(side="left")
        self.save_button = ttk.Button(footer, command=self.save); self.save_button.pack(side="right"); self._translate()

    def _translate(self) -> None:
        t = self.translator.text; self.root.title(t("app.title")); self.refresh_button.config(text=t("action.refresh")); self.choose_root_button.config(text=t("action.choose_directory")); self.about_button.config(text=t("action.about")); self.save_button.config(text=t("action.save"))
        self.language_label.config(text=t("label.language")); self.labels["farmer"].config(text=t("label.farmer")); self.labels["farm"].config(text=t("label.farm")); self.labels["favorite"].config(text=t("label.favorite")); self.animals_label.config(text=t("label.animals")); self.farmhands_label.config(text=t("label.farmhands"))
        self.animals.heading("species", text=t("animal.species")); self.animals.heading("name", text=t("animal.name"))
        self.farmhand_labels["farmer"].config(text=t("farmhand.farmer")); self.farmhand_labels["favorite"].config(text=t("farmhand.favorite"))
        if self.loaded is not None:
            originals = {str(animal.index): animal for animal in self.loaded.animals}
            for item in self.animals.get_children(): self.animals.set(item, "species", self.translator.animal_type(originals[item].species))

    def _change_language(self, _event=None) -> None:
        index = self.language_box.current()
        if index >= 0:
            self.language.set(LANGUAGES[index][0])
            self.translator.set_language(self.language.get())
        self._translate()
        self._render_status()

    def _render_status(self) -> None:
        if self.loaded is not None:
            self.status.set(self.translator.text("status.loaded", name=self.loaded.farmer_name))
        elif self.paths:
            self.status.set(str(self.save_root))
        else:
            self.status.set(f"{self.translator.text('status.no_saves')}: {self.save_root}")

    def choose_save_root(self) -> None:
        selected = filedialog.askdirectory(parent=self.root, initialdir=self.save_root)
        if selected:
            self.save_root = Path(selected)
            self.refresh_saves()

    def show_about(self) -> None:
        window = tk.Toplevel(self.root)
        window.title(self.translator.text("about.title"))
        window.resizable(False, False)
        body = ttk.Frame(window, padding=12); body.pack(fill="both", expand=True)
        links = (
            ("about.author", "fyihang", AUTHOR_URL),
            ("about.repository", "fyihang/StardewValleyTool", REPOSITORY_URL),
            ("about.version", APP_VERSION, VERSION_URL),
        )
        for row, (label_key, value, url) in enumerate(links):
            ttk.Label(body, text=self.translator.text(label_key)).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
            link = ttk.Label(body, text=value, cursor="hand2")
            link.grid(row=row, column=1, sticky="w", pady=4)
            link.bind("<Button-1>", lambda _event, target=url: open_url(target))

    def refresh_saves(self) -> None:
        self.paths = discover_saves(self.save_root); self.save_list.delete(0, "end")
        for item in self.paths: self.save_list.insert("end", item.directory.name)
        self.loaded = self.selected = None; self._render_status(); self._update_save_state()

    def _select_save(self, _event=None) -> None:
        if not self.save_list.curselection(): return
        self.selected = self.paths[self.save_list.curselection()[0]]
        try:
            self.loaded = load_save(self.selected); values = self.loaded
            for key, value in (("farmer", values.farmer_name), ("farm", values.farm_name), ("favorite", values.favorite_thing)): self.vars[key].set(value)
            self.animals.delete(*self.animals.get_children())
            for animal in values.animals: self.animals.insert("", "end", iid=str(animal.index), values=(self.translator.animal_type(animal.species), animal.name))
            self._farmhands = list(values.farmhands); self._active_farmhand = None
            if self._farmhands:
                self.farmhands_frame.grid(); self.farmhand_box["values"] = tuple(hand.farmer_name for hand in self._farmhands); self.farmhand_box.current(0); self._select_farmhand()
            else:
                self.farmhands_frame.grid_remove(); self.farmhand_box.set("")
            self._render_status()
        except (OSError, ValueError, SaveConsistencyError) as error: messagebox.showerror(self.translator.text("error.title"), str(error))
        self._update_save_state()

    def _edit_animal(self, event) -> None:
        item = self.animals.identify_row(event.y); column = self.animals.identify_column(event.x)
        if not item or column != "#2": return
        value = self.animals.item(item, "values")[1]; dialog = simpledialog.askstring(self.translator.text("label.animals"), self.translator.text("animal.name"), initialvalue=value, parent=self.root)
        if dialog is not None: self.animals.set(item, "name", dialog); self._update_save_state()

    def _store_active_farmhand(self) -> None:
        if self._active_farmhand is None:
            return
        current = self._farmhands[self._active_farmhand]
        self._farmhands[self._active_farmhand] = Farmhand(current.index, self.farmhand_vars["farmer"].get(), current.farm_name, self.farmhand_vars["favorite"].get())

    def _select_farmhand(self, _event=None) -> None:
        self._store_active_farmhand(); index = self.farmhand_box.current()
        if index < 0:
            return
        self._active_farmhand = index; hand = self._farmhands[index]
        self.farmhand_vars["farmer"].set(hand.farmer_name); self.farmhand_vars["favorite"].set(hand.favorite_thing)

    def _current(self) -> SaveData:
        assert self.loaded is not None
        original_animals = {str(animal.index): animal for animal in self.loaded.animals}
        animals = tuple(replace(original_animals[item], name=self.animals.set(item, "name")) for item in self.animals.get_children())
        horse = next((animal.name for animal in animals if animal.kind == "horse"), None)
        self._store_active_farmhand()
        return SaveData(self.vars["farmer"].get(), self.vars["farm"].get(), self.vars["favorite"].get(), horse, animals, tuple(self._farmhands))

    def _update_save_state(self) -> None:
        enabled = self.loaded is not None and self._current() != self.loaded
        self.save_button.config(state="normal" if enabled else "disabled")

    def save(self) -> None:
        if self.loaded is None or self.selected is None: return
        if not messagebox.askyesno(self.translator.text("app.title"), self.translator.text("dialog.confirm_save"), parent=self.root): return
        try:
            backup = save_changes(self.selected, self.loaded, self._current()); messagebox.showinfo(self.translator.text("app.title"), self.translator.text("status.saved_with_backup", backup=backup), parent=self.root); self._select_save()
        except SaveWriteError as error: messagebox.showerror(self.translator.text("error.title"), str(error), parent=self.root)


def main() -> None:
    root = tk.Tk(); SaveManagerApp(root); root.mainloop()
