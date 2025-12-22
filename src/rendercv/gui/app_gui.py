# German Ahmed Cruz Ramírez
# https://www.linkedin.com/in/german-cruz-ram-in24/
# Managua, Nicaragua 22/12/2025

import pathlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Any, cast

from rendercv.cli.render_command.progress_panel import ProgressPanel
from rendercv.cli.render_command.run_rendercv import run_rendercv
from rendercv.exception import RenderCVUserError


class GuiProgressPanel:
    def __init__(self, log_widget: scrolledtext.ScrolledText):
        self.log_widget = log_widget
        self.completed_steps = []

    def update_progress(
        self, time_took: str, message: str, paths: list[pathlib.Path]
    ) -> None:
        path_str = ""
        if paths:
            path_str = " (" + ", ".join([p.name for p in paths]) + ")"

        text = f"✓ {time_took} ms - {message}{path_str}\n"
        self._append_text(text)

    def finish_progress(self) -> None:
        self._append_text("\nYour CV is ready!\n")

    def print_progress_panel(self, title: str) -> None:
        pass

    def print_user_error(self, user_error: RenderCVUserError) -> None:
        self._append_text(f"\nERROR: {user_error.message}\n")

    def print_validation_errors(self, errors: list[Any]) -> None:
        self._append_text("\nValidation Errors:\n")
        for error in errors:
            loc = ".".join(str(loc_part) for loc_part in error.location)
            self._append_text(
                f"- Location: {loc}\n  Input: {error.input}\n  Message:"
                f" {error.message}\n"
            )

    def clear(self) -> None:
        pass

    def _append_text(self, text: str):
        self.log_widget.configure(state="normal")
        self.log_widget.insert(tk.END, text)
        self.log_widget.see(tk.END)
        self.log_widget.configure(state="disabled")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class RenderCVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RenderCV GUI")
        self.root.geometry("600x500")

        self.file_path = tk.StringVar()

        # File Selection
        frame_file = tk.Frame(root)
        frame_file.pack(pady=10, padx=10, fill=tk.X)

        lbl_file = tk.Label(frame_file, text="Input YAML File:")
        lbl_file.pack(side=tk.LEFT)

        entry_file = tk.Entry(frame_file, textvariable=self.file_path, width=40)
        entry_file.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        btn_browse = tk.Button(frame_file, text="Browse", command=self.browse_file)
        btn_browse.pack(side=tk.LEFT)

        # Render Button
        btn_render = tk.Button(
            root,
            text="Render CV",
            command=self.start_render,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        btn_render.pack(pady=10)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(root, state="disabled", height=20)
        self.log_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def start_render(self):
        input_file = self.file_path.get()
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        self.log_area.configure(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, f"Processing {input_file}...\n\n")
        self.log_area.configure(state="disabled")

        thread = threading.Thread(target=self.run_process, args=(input_file,))
        thread.start()

    def run_process(self, input_file):
        progress_panel = GuiProgressPanel(self.log_area)
        try:
            run_rendercv(
                pathlib.Path(input_file),
                cast(ProgressPanel, progress_panel),
            )
        except Exception as e:
            progress_panel._append_text(f"\nUnexpected Error: {e}\n")


def main():
    root = tk.Tk()
    RenderCVApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()