"""Drag-and-drop GUI: drop files/folders across multiple passes, then build
a single CD-ROM .iso from everything queued up."""

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
        self.geometry("480x420")
        self.minsize(380, 320)

        self.queued_paths = []

        self.drop_label = tk.Label(
            self,
            text="Drag files or folders here\n\nor click to add",
            relief="groove",
            borderwidth=2,
            font=("TkDefaultFont", 14),
            justify="center",
            cursor="hand2",
        )
        self.drop_label.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_label.bind("<Button-1>", self._on_click)

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.clear_button = tk.Button(button_frame, text="Clear", command=self._on_clear)
        self.clear_button.pack(side="left")
        self.build_button = tk.Button(
            button_frame, text="Build ISO...", command=self._on_build, state="disabled"
        )
        self.build_button.pack(side="right")

        self.status = tk.Label(self, text="", wraplength=440, justify="left")
        self.status.pack(fill="x", padx=20, pady=(0, 20))

    def _on_click(self, _event):
        paths = filedialog.askopenfilenames(title="Choose file(s) to add")
        if paths:
            self._queue(list(paths))

    def _on_drop(self, event):
        paths = list(self.tk.splitlist(event.data))
        if paths:
            self._queue(paths)

    def _queue(self, paths):
        for path in paths:
            if path not in self.queued_paths:
                self.queued_paths.append(path)
                self.listbox.insert("end", Path(path).name)

        count = len(self.queued_paths)
        self.status.config(text=f"{count} item{'s' if count != 1 else ''} queued.", fg="black")
        self.build_button.config(state="normal" if self.queued_paths else "disabled")

    def _on_clear(self):
        self.queued_paths = []
        self.listbox.delete(0, "end")
        self.build_button.config(state="disabled")
        self.status.config(text="", fg="black")

    def _on_build(self):
        first = Path(self.queued_paths[0])
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
            result_path = build_iso(self.queued_paths, output_path)
        except IsoBuildError as e:
            self.status.config(text=f"Failed: {e}", fg="red")
            messagebox.showerror(WINDOW_TITLE, str(e))
        except Exception as e:
            traceback.print_exc()
            self.status.config(text=f"Unexpected error: {e}", fg="red")
            messagebox.showerror(WINDOW_TITLE, f"Unexpected error:\n{e}")
        else:
            self.status.config(text=f"Saved: {result_path}", fg="dark green")
            self._on_clear()


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
