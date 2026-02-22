from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core.router import ParserRouter
from .core.storage import MarkdownStorage
from .core.utils import detect_quartz_content_dir


class XUrlIngestorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("X URL to Quartz Markdown")
        self.geometry("840x580")
        self.minsize(760, 520)

        self.router = ParserRouter()
        self.log_queue: queue.Queue[str] = queue.Queue()

        default_dir = detect_quartz_content_dir()
        self.url_var = tk.StringVar()
        self.content_dir_var = tk.StringVar(value=str(default_dir))
        self.filename_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")

        self._build_widgets()
        self.after(100, self._drain_logs)

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="X URL").grid(row=0, column=0, sticky="w")
        url_entry = ttk.Entry(frame, textvariable=self.url_var)
        url_entry.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(2, 10))
        url_entry.focus_set()

        ttk.Label(frame, text="Quartz content folder").grid(row=2, column=0, sticky="w")
        dir_entry = ttk.Entry(frame, textvariable=self.content_dir_var)
        dir_entry.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(2, 10))
        ttk.Button(frame, text="Browse", command=self._browse_folder).grid(row=3, column=3, padx=(8, 0))

        ttk.Label(frame, text="Optional filename hint").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.filename_var).grid(
            row=5, column=0, columnspan=4, sticky="ew", pady=(2, 10)
        )

        self.import_button = ttk.Button(frame, text="Fetch and Create Markdown", command=self._run_ingest)
        self.import_button.grid(row=6, column=0, sticky="w", pady=(2, 10))

        ttk.Button(frame, text="Open content folder", command=self._open_content_folder).grid(
            row=6, column=1, sticky="w", padx=(8, 0), pady=(2, 10)
        )

        ttk.Label(frame, textvariable=self.status_var).grid(row=6, column=2, columnspan=2, sticky="e")

        ttk.Label(frame, text="Log").grid(row=7, column=0, sticky="w")
        self.log_box = tk.Text(frame, height=18, wrap="word")
        self.log_box.grid(row=8, column=0, columnspan=4, sticky="nsew", pady=(4, 0))

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.log_box.yview)
        scrollbar.grid(row=8, column=4, sticky="ns", pady=(4, 0))
        self.log_box.configure(yscrollcommand=scrollbar.set)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=0)
        frame.rowconfigure(8, weight=1)

    def _browse_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.content_dir_var.get() or str(Path.cwd()))
        if selected:
            self.content_dir_var.set(selected)

    def _open_content_folder(self) -> None:
        target = Path(self.content_dir_var.get().strip())
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)

        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
            return
        messagebox.showinfo("Info", f"Open this folder manually:\n{target}")

    def _run_ingest(self) -> None:
        url = self.url_var.get().strip()
        content_dir = self.content_dir_var.get().strip()
        filename_hint = self.filename_var.get().strip()

        if not url:
            messagebox.showwarning("Missing URL", "Please paste an X URL first.")
            return
        if not content_dir:
            messagebox.showwarning("Missing folder", "Please set Quartz content folder.")
            return

        self.import_button.configure(state=tk.DISABLED)
        self.status_var.set("Working...")
        self._log(f"URL: {url}")
        self._log(f"Target: {content_dir}")

        thread = threading.Thread(
            target=self._ingest_worker,
            args=(url, content_dir, filename_hint),
            daemon=True,
        )
        thread.start()

    def _ingest_worker(self, url: str, content_dir: str, filename_hint: str) -> None:
        try:
            result = self.router.route(url)
            if not result.success:
                self.log_queue.put(f"[ERROR] {result.error}")
                self.log_queue.put("__DONE_ERROR__")
                return

            storage = MarkdownStorage(Path(content_dir))
            saved_path = storage.save(result=result, filename_hint=filename_hint)
            self.log_queue.put(f"[OK] Markdown created: {saved_path}")
            self.log_queue.put("__DONE_SUCCESS__")
        except Exception as exc:  # noqa: BLE001
            self.log_queue.put(f"[ERROR] Unexpected failure: {exc}")
            self.log_queue.put("__DONE_ERROR__")

    def _drain_logs(self) -> None:
        try:
            while True:
                item = self.log_queue.get_nowait()
                if item == "__DONE_SUCCESS__":
                    self.import_button.configure(state=tk.NORMAL)
                    self.status_var.set("Done")
                    messagebox.showinfo("Done", "Markdown file created in content folder.")
                    continue
                if item == "__DONE_ERROR__":
                    self.import_button.configure(state=tk.NORMAL)
                    self.status_var.set("Failed")
                    continue
                self._log(item)
        except queue.Empty:
            pass
        self.after(120, self._drain_logs)

    def _log(self, message: str) -> None:
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)


def run_app() -> None:
    app = XUrlIngestorApp()
    app.mainloop()

