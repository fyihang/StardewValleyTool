from dataclasses import replace
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from discovery import default_save_root, discover_saves
from i18n import Translator
from models import Animal, Farmhand, SaveData, SavePaths
from reader import SaveConsistencyError, load_save
from writer import SaveWriteError, save_changes


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
        self._build()
        self.refresh_saves()

    def _build(self) -> None:
        self.root.minsize(760, 480)
        outer = ttk.Frame(self.root, padding=12); outer.pack(fill="both", expand=True)
        toolbar = ttk.Frame(outer); toolbar.pack(fill="x")
        self.refresh_button = ttk.Button(toolbar, command=self.refresh_saves); self.refresh_button.pack(side="left")
        ttk.Label(toolbar, textvariable=tk.StringVar(value="")).pack(side="left", padx=8)
        self.language = tk.StringVar(value="en")
        self.language_box = ttk.Combobox(toolbar, width=10, state="readonly", values=("English", "中文"))
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
        self.farmhands_label = ttk.Label(right); self.farmhands_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 3))
        self.farmhands = ttk.Treeview(right, columns=("farmer", "farm", "favorite"), show="headings", height=4); self.farmhands.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.farmhands.column("farmer", width=140); self.farmhands.column("farm", width=140); self.farmhands.column("favorite", width=180); self.farmhands.bind("<Double-1>", self._edit_farmhand)
        right.rowconfigure(4, weight=1); right.rowconfigure(6, weight=1)
        self.save_button = ttk.Button(outer, command=self.save); self.save_button.pack(anchor="e"); self._translate()

    def _translate(self) -> None:
        t = self.translator.text; self.root.title(t("app.title")); self.refresh_button.config(text=t("action.refresh")); self.save_button.config(text=t("action.save"))
        self.language_label.config(text=t("label.language")); self.labels["farmer"].config(text=t("label.farmer")); self.labels["farm"].config(text=t("label.farm")); self.labels["favorite"].config(text=t("label.favorite")); self.animals_label.config(text=t("label.animals")); self.farmhands_label.config(text=t("label.farmhands"))
        self.animals.heading("species", text=t("animal.species")); self.animals.heading("name", text=t("animal.name"))
        self.farmhands.heading("farmer", text=t("farmhand.farmer")); self.farmhands.heading("farm", text=t("farmhand.farm")); self.farmhands.heading("favorite", text=t("farmhand.favorite"))

    def _change_language(self, _event=None) -> None:
        self.translator.set_language("zh" if self.language_box.current() == 1 else "en"); self._translate()

    def refresh_saves(self) -> None:
        self.paths = discover_saves(self.save_root); self.save_list.delete(0, "end")
        for item in self.paths: self.save_list.insert("end", item.directory.name)
        self.status.set(str(self.save_root) if self.paths else f"No valid saves found in {self.save_root}")
        self.loaded = self.selected = None; self._update_save_state()

    def _select_save(self, _event=None) -> None:
        if not self.save_list.curselection(): return
        self.selected = self.paths[self.save_list.curselection()[0]]
        try:
            self.loaded = load_save(self.selected); values = self.loaded
            for key, value in (("farmer", values.farmer_name), ("farm", values.farm_name), ("favorite", values.favorite_thing)): self.vars[key].set(value)
            self.animals.delete(*self.animals.get_children())
            for animal in values.animals: self.animals.insert("", "end", iid=str(animal.index), values=(animal.species, animal.name))
            self.farmhands.delete(*self.farmhands.get_children())
            for farmhand in values.farmhands: self.farmhands.insert("", "end", iid=str(farmhand.index), values=(farmhand.farmer_name, farmhand.farm_name, farmhand.favorite_thing))
            self.status.set(self.translator.text("status.loaded", name=values.farmer_name))
        except (OSError, ValueError, SaveConsistencyError) as error: messagebox.showerror(self.translator.text("error.title"), str(error))
        self._update_save_state()

    def _edit_animal(self, event) -> None:
        item = self.animals.identify_row(event.y); column = self.animals.identify_column(event.x)
        if not item or column != "#2": return
        value = self.animals.item(item, "values")[1]; dialog = simpledialog.askstring(self.translator.text("label.animals"), self.translator.text("animal.name"), initialvalue=value, parent=self.root)
        if dialog is not None: self.animals.set(item, "name", dialog); self._update_save_state()

    def _edit_farmhand(self, event) -> None:
        item = self.farmhands.identify_row(event.y); column = self.farmhands.identify_column(event.x)
        if not item or column not in ("#1", "#2", "#3"): return
        key = {"#1": "farmer", "#2": "farm", "#3": "favorite"}[column]
        value = self.farmhands.set(item, key); dialog = simpledialog.askstring(self.translator.text("label.farmhands"), self.translator.text(f"farmhand.{key}"), initialvalue=value, parent=self.root)
        if dialog is not None: self.farmhands.set(item, key, dialog); self._update_save_state()

    def _current(self) -> SaveData:
        assert self.loaded is not None
        original_animals = {str(animal.index): animal for animal in self.loaded.animals}
        animals = tuple(replace(original_animals[item], name=self.animals.set(item, "name")) for item in self.animals.get_children())
        horse = next((animal.name for animal in animals if animal.kind == "horse"), None)
        farmhands = tuple(Farmhand(int(item), self.farmhands.set(item, "farmer"), self.farmhands.set(item, "farm"), self.farmhands.set(item, "favorite")) for item in self.farmhands.get_children())
        return SaveData(self.vars["farmer"].get(), self.vars["farm"].get(), self.vars["favorite"].get(), horse, animals, farmhands)

    def _update_save_state(self) -> None:
        enabled = self.loaded is not None and self._current() != self.loaded
        self.save_button.config(state="normal" if enabled else "disabled")

    def save(self) -> None:
        if self.loaded is None or self.selected is None: return
        if not messagebox.askyesno(self.translator.text("app.title"), "Confirm Stardew Valley is closed before saving.", parent=self.root): return
        try:
            backup = save_changes(self.selected, self.loaded, self._current()); messagebox.showinfo(self.translator.text("app.title"), f"Saved successfully. Backup: {backup}", parent=self.root); self._select_save()
        except SaveWriteError as error: messagebox.showerror(self.translator.text("error.title"), str(error), parent=self.root)


def main() -> None:
    root = tk.Tk(); SaveManagerApp(root); root.mainloop()
