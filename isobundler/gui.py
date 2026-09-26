"""Drag-and-drop GUI: drop files/folders, get a CD-ROM .iso out."""

import traceback
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD

from .builder import IsoBuildError, build_iso

WINDOW_TITLE = "ISO Bundler"


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("480x320")
        self.minsize(380, 260)

        self.drop_label = tk.Label(
            self,
            text="Drag files or a folder here\n\nor click to choose",
            relief="groove",
            borderwidth=2,
            font=("TkDefaultFont", 14),
            justify="center",
            cursor="hand2",
        )
        self.drop_label.pack(expand=True, fill="both", padx=20, pady=20)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_label.bind("<Button-1>", self._on_click)

        self.status = tk.Label(self, text="", wraplength=440, justify="left")
        self.status.pack(fill="x", padx=20, pady=(0, 20))

    def _on_click(self, _event):
        paths = filedialog.askopenfilenames(title="Choose file(s) to bundle into an ISO")
        if paths:
            self._build(list(paths))

    def _on_drop(self, event):
        paths = list(self.tk.splitlist(event.data))
        if paths:
            self._build(paths)

    def _build(self, paths):
        first = Path(paths[0])
        default_name = first.stem if first.is_file() else first.name
        output_path = filedialog.asksaveasfilename(
            title="Save ISO as",
            defaultextension=".iso",
            initialfile=f"{default_name}.iso",
            filetypes=[("ISO image", "*.iso")],
        )
        if not output_path:
            return

        self.status.config(text="Building ISO...", fg="black")
        self.update_idletasks()
        try:
            result_path = build_iso(paths, output_path)
        except IsoBuildError as e:
            self.status.config(text=f"Failed: {e}", fg="red")
            messagebox.showerror(WINDOW_TITLE, str(e))
        except Exception as e:
            traceback.print_exc()
            self.status.config(text=f"Unexpected error: {e}", fg="red")
            messagebox.showerror(WINDOW_TITLE, f"Unexpected error:\n{e}")
        else:
            self.status.config(text=f"Saved: {result_path}", fg="dark green")


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
