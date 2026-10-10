import os
import sys
import glob
import re
import shutil
import csv
import json
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

# Import prompts and default skip set from organize_images
try:
    from organize_images import (
        PROMPTS, SKIPPED_TIMESTAMPS, sanitize_filename,
        load_prompts, save_prompts, parse_prompts_from_text, format_prompts_to_text
    )
except ImportError:
    # Fallback if imported from another location
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from organize_images import (
        PROMPTS, SKIPPED_TIMESTAMPS, sanitize_filename,
        load_prompts, save_prompts, parse_prompts_from_text, format_prompts_to_text
    )

# Set CustomTkinter theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PromptsManagerDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("📝 Prompt Manager & Paste Input")
        self.geometry("900x680")
        self.minsize(750, 520)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._populate_current()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#18181b")
        header.pack(fill="x", padx=0, pady=0)

        top_box = ctk.CTkFrame(header, fg_color="transparent")
        top_box.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(
            top_box,
            text="📝 Prompts Manager & Input",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f4f4f5"
        ).pack(side="left")

        self.count_badge = ctk.CTkLabel(
            top_box,
            text="0 Prompts Detected",
            fg_color="#27272a",
            corner_radius=6,
            padx=12,
            pady=4,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.count_badge.pack(side="right")

        # Instruction banner
        info_banner = ctk.CTkFrame(self, fg_color="#202024", corner_radius=8)
        info_banner.pack(fill="x", padx=16, pady=(10, 6))

        info_text = (
            "💡 How to input: Paste prompts below with timestamps like [00:00] Description... "
            "Prompts can span multiple lines.\n"
            "You can also click 'Paste from Clipboard', load from a .txt / .json file, or type/edit directly."
        )
        ctk.CTkLabel(
            info_banner,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            justify="left"
        ).pack(anchor="w", padx=12, pady=8)

        # Toolbar Frame
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=(2, 6))

        ctk.CTkButton(
            toolbar,
            text="📋 Paste from Clipboard",
            width=160,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(weight="bold"),
            command=self._paste_from_clipboard
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="📂 Load File (.txt/.json)",
            width=150,
            fg_color="#334155",
            hover_color="#475569",
            command=self._load_file
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="💾 Export (.txt)",
            width=110,
            fg_color="#334155",
            hover_color="#475569",
            command=self._export_file
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="🔄 Reload Current",
            width=120,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._populate_current
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="🧹 Clear",
            width=75,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=self._clear_text
        ).pack(side="right")

        # Main Text Editor
        text_frame = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=8)
        text_frame.pack(fill="both", expand=True, padx=16, pady=4)

        self.textbox = ctk.CTkTextbox(
            text_frame,
            fg_color="#18181b",
            text_color="#f4f4f5",
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            undo=True
        )
        self.textbox.pack(fill="both", expand=True, padx=8, pady=8)
        self.textbox.bind("<KeyRelease>", lambda e: self._update_count())

        # Footer Actions
        footer = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=0)
        footer.pack(fill="x", side="bottom", padx=0, pady=0)

        f_inner = ctk.CTkFrame(footer, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=10)

        self.apply_btn = ctk.CTkButton(
            f_inner,
            text="✅ Apply Prompts to Organizer",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=220,
            command=self._apply_and_close
        )
        self.apply_btn.pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            f_inner,
            text="Cancel",
            width=90,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self.destroy
        ).pack(side="right")

    def _populate_current(self):
        text_content = format_prompts_to_text(self.parent.prompts_list)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text_content)
        self._update_count()

    def _update_count(self):
        raw = self.textbox.get("1.0", "end").strip()
        parsed = parse_prompts_from_text(raw)
        cnt = len(parsed)
        self.count_badge.configure(text=f"{cnt} Prompts Detected")
        self.apply_btn.configure(text=f"✅ Apply {cnt} Prompts" if cnt > 0 else "✅ Apply Prompts")
        return parsed

    def _paste_from_clipboard(self):
        try:
            cb_text = self.clipboard_get()
            if cb_text:
                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", cb_text)
                self._update_count()
        except Exception as e:
            messagebox.showwarning("Clipboard", f"Could not read clipboard: {e}")

    def _clear_text(self):
        self.textbox.delete("1.0", "end")
        self._update_count()

    def _load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text & JSON Files", "*.txt *.json"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            if path.endswith(".json"):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prompts = [(item["timestamp"], item["prompt"]) for item in data if "timestamp" in item and "prompt" in item]
                    text_content = format_prompts_to_text(prompts)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    text_content = f.read()
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", text_content)
            self._update_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _export_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("JSON File", "*.json")]
        )
        if not path:
            return
        try:
            raw = self.textbox.get("1.0", "end").strip()
            parsed = parse_prompts_from_text(raw)
            if path.endswith(".json"):
                save_prompts(parsed, target_path=path)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(format_prompts_to_text(parsed))
            messagebox.showinfo("Exported", f"Successfully exported {len(parsed)} prompts to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {e}")

    def _apply_and_close(self):
        parsed = self._update_count()
        if not parsed:
            messagebox.showwarning("No Prompts", "No valid prompts were found in the text box.\nPlease check your format.")
            return

        # Save to current_prompts.json in workspace and source directory
        try:
            save_prompts(parsed)
            src_dir = self.parent.source_dir_var.get()
            if os.path.exists(src_dir):
                save_prompts(parsed, os.path.join(src_dir, "current_prompts.json"))
        except Exception as e:
            print("Warning saving current_prompts.json:", e)

        # Update parent state
        self.parent.prompts_list = parsed
        if hasattr(self.parent, "prompts_btn"):
            self.parent.prompts_btn.configure(text=f"📝 Prompts ({len(parsed)})")
        self.destroy()

        # Trigger preview update
        self.parent._scan_and_preview()
        messagebox.showinfo(
            "Prompts Updated",
            f"Successfully applied {len(parsed)} prompts!\nTimeline preview has been refreshed."
        )


class ImageOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Prompt & Timeline Organizer")
        self.geometry("1220x760")
        self.minsize(1050, 620)

        # Base directories
        default_dir = os.path.dirname(os.path.abspath(__file__))
        self.source_dir_var = tk.StringVar(value=default_dir)
        self.output_name_var = tk.StringVar(value="organized_images")
        self.archive_name_var = tk.StringVar(value="original_images")
        self.archive_enabled_var = tk.BooleanVar(value=True)
        self.action_var = tk.StringVar(value="copy")
        self.skipped_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready. Click 'Scan & Match' to preview.")

        # Data state - load active prompts from current_prompts.json or default
        self.prompts_list = load_prompts(default_dir)
        self.mapped_items = []
        self.is_processing = False
        self.current_thumbnail = None

        self._create_layout()
        self._scan_and_preview()

    def _create_layout(self):
        # 1. Header Frame
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#18181b")
        header.pack(fill="x", padx=0, pady=0)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=12)

        title_lbl = ctk.CTkLabel(
            title_box,
            text="✨ Image Timeline & Prompt Organizer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f4f4f5"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Chronological alignment, smart prompt renaming & organization",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1aa"
        )
        subtitle_lbl.pack(anchor="w")

        # Top right badges
        badge_box = ctk.CTkFrame(header, fg_color="transparent")
        badge_box.pack(side="right", padx=20, pady=12)

        self.count_badge = ctk.CTkLabel(
            badge_box,
            text="0 Images Matched",
            fg_color="#27272a",
            corner_radius=6,
            padx=12,
            pady=4,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.count_badge.pack(side="right")

        self.prompts_btn = ctk.CTkButton(
            badge_box,
            text=f"📝 Input / Paste Prompts ({len(self.prompts_list)})",
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_prompts_manager
        )
        self.prompts_btn.pack(side="right", padx=(0, 10))

        # 2. Controls & Configuration Card
        controls_card = ctk.CTkFrame(self, fg_color="#202024", corner_radius=10)
        controls_card.pack(fill="x", padx=16, pady=(12, 6))

        # Row 1: Source, Output & Archive
        r1 = ctk.CTkFrame(controls_card, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(r1, text="Source Folder:", width=95, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.src_entry = ctk.CTkEntry(r1, textvariable=self.source_dir_var, font=ctk.CTkFont(size=12))
        self.src_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(r1, text="Browse...", width=75, command=self._browse_source).pack(side="left", padx=(0, 14))

        ctk.CTkLabel(r1, text="Organized Folder:", width=110, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.out_entry = ctk.CTkEntry(r1, textvariable=self.output_name_var, width=150, font=ctk.CTkFont(size=12))
        self.out_entry.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(r1, text="Archive Folder:", width=95, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.arch_entry = ctk.CTkEntry(r1, textvariable=self.archive_name_var, width=150, font=ctk.CTkFont(size=12))
        self.arch_entry.pack(side="left", padx=(0, 6))

        # Row 2: Mode, Archive Checkbox, Skips & Action Buttons
        r2 = ctk.CTkFrame(controls_card, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(r2, text="Mode:", width=45, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.mode_seg = ctk.CTkSegmentedButton(
            r2,
            values=["Copy (Safe)", "Move"],
            command=self._on_mode_change,
            width=135
        )
        self.mode_seg.set("Copy (Safe)")
        self.mode_seg.pack(side="left", padx=(0, 12))

        self.archive_chk = ctk.CTkCheckBox(
            r2,
            text="Archive originals (clean main)",
            variable=self.archive_enabled_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            checkmark_color="#ffffff",
            fg_color="#0284c7",
            hover_color="#0369a1"
        )
        self.archive_chk.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(r2, text="Skip Timestamps:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.skip_entry = ctk.CTkEntry(r2, textvariable=self.skipped_var, width=130, font=ctk.CTkFont(size=12))
        self.skip_entry.pack(side="left", padx=(6, 12))

        self.prompts_card_btn = ctk.CTkButton(
            r2,
            text="📝 Prompts",
            width=90,
            fg_color="#334155",
            hover_color="#475569",
            command=self._open_prompts_manager
        )
        self.prompts_card_btn.pack(side="left", padx=(0, 6))

        self.scan_btn = ctk.CTkButton(
            r2,
            text="🔄 Scan & Match",
            width=110,
            fg_color="#334155",
            hover_color="#475569",
            command=self._scan_and_preview
        )
        self.scan_btn.pack(side="left", padx=(0, 6))

        self.run_btn = ctk.CTkButton(
            r2,
            text="▶ Run Organization",
            width=145,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(weight="bold"),
            command=self._start_organization
        )
        self.run_btn.pack(side="left", padx=(0, 6))

        self.open_orig_btn = ctk.CTkButton(
            r2,
            text="📁 Open Originals",
            width=105,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._open_originals_dir
        )
        self.open_orig_btn.pack(side="right", padx=(4, 0))

        self.open_btn = ctk.CTkButton(
            r2,
            text="📂 Open Output",
            width=105,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._open_output_dir
        )
        self.open_btn.pack(side="right")

        # 3. Middle Paned Area (Table + Inspector)
        middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        middle_frame.pack(fill="both", expand=True, padx=16, pady=6)

        # Left: Table Frame
        table_frame = ctk.CTkFrame(middle_frame, fg_color="#18181b", corner_radius=10)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Setup custom styled ttk.Treeview
        self._setup_treeview(table_frame)

        # Right: Preview / Details Inspector
        self.inspector = ctk.CTkFrame(middle_frame, width=350, fg_color="#202024", corner_radius=10)
        self.inspector.pack(side="right", fill="y", padx=(0, 0))
        self.inspector.pack_propagate(False)

        self._setup_inspector()

        # 4. Footer & Progress Bar
        footer = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=0)
        footer.pack(fill="x", side="bottom", padx=0, pady=0)

        self.progress_bar = ctk.CTkProgressBar(footer, height=6, fg_color="#27272a", progress_color="#38bdf8")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(8, 4))

        status_box = ctk.CTkFrame(footer, fg_color="transparent")
        status_box.pack(fill="x", padx=16, pady=(0, 8))

        self.status_lbl = ctk.CTkLabel(
            status_box,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            anchor="w"
        )
        self.status_lbl.pack(side="left")

    def _setup_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="#1e1e24",
            foreground="#f4f4f5",
            fieldbackground="#1e1e24",
            rowheight=28,
            font=("Segoe UI", 9)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#141418",
            foreground="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=5
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#0284c7")],
            foreground=[("selected", "#ffffff")]
        )

        columns = ("index", "timestamp", "download_time", "orig_file", "new_name")
        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        self.tree.heading("index", text="#")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("download_time", text="Downloaded Time")
        self.tree.heading("orig_file", text="Original Image")
        self.tree.heading("new_name", text="Renamed Target")

        self.tree.column("index", width=40, anchor="center")
        self.tree.column("timestamp", width=85, anchor="center")
        self.tree.column("download_time", width=135, anchor="center")
        self.tree.column("orig_file", width=220, anchor="w")
        self.tree.column("new_name", width=380, anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _setup_inspector(self):
        ins_title = ctk.CTkLabel(
            self.inspector,
            text="🔍 Image Inspector",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        ins_title.pack(anchor="w", padx=14, pady=(12, 6))

        # Thumbnail canvas/label
        self.thumb_container = ctk.CTkFrame(self.inspector, width=320, height=180, fg_color="#141418", corner_radius=8)
        self.thumb_container.pack(padx=14, pady=4)
        self.thumb_container.pack_propagate(False)

        self.thumb_label = ctk.CTkLabel(self.thumb_container, text="No image selected", text_color="#71717a")
        self.thumb_label.pack(expand=True)

        # Metadata labels
        meta_frame = ctk.CTkFrame(self.inspector, fg_color="transparent")
        meta_frame.pack(fill="x", padx=14, pady=8)

        self.lbl_sel_ts = ctk.CTkLabel(meta_frame, text="Timestamp: -", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38bdf8", anchor="w")
        self.lbl_sel_ts.pack(fill="x")

        self.lbl_sel_time = ctk.CTkLabel(meta_frame, text="Created: -", font=ctk.CTkFont(size=11), text_color="#a1a1aa", anchor="w")
        self.lbl_sel_time.pack(fill="x")

        self.lbl_sel_file = ctk.CTkLabel(meta_frame, text="File: -", font=ctk.CTkFont(size=11), text_color="#a1a1aa", anchor="w")
        self.lbl_sel_file.pack(fill="x")

        ctk.CTkLabel(self.inspector, text="Matched Prompt Text:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#f4f4f5").pack(anchor="w", padx=14, pady=(6, 2))

        self.prompt_text_box = ctk.CTkTextbox(
            self.inspector,
            height=180,
            fg_color="#18181b",
            font=ctk.CTkFont(size=11),
            text_color="#d4d4d8",
            wrap="word"
        )
        self.prompt_text_box.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.prompt_text_box.configure(state="disabled")

    def _browse_source(self):
        folder = filedialog.askdirectory(initialdir=self.source_dir_var.get())
        if folder:
            self.source_dir_var.set(folder)
            folder_prompts = load_prompts(folder)
            if folder_prompts:
                self.prompts_list = folder_prompts
                if hasattr(self, "prompts_btn"):
                    self.prompts_btn.configure(text=f"📝 Input / Paste Prompts ({len(self.prompts_list)})")
            self._scan_and_preview()

    def _open_prompts_manager(self):
        PromptsManagerDialog(self)

    def _on_mode_change(self, value):
        self.action_var.set("copy" if "Copy" in value else "move")

    def _get_skipped_set(self):
        raw = self.skipped_var.get()
        items = set()
        for piece in raw.split(","):
            piece = piece.strip().strip("[]")
            if piece:
                items.add(f"[{piece}]")
        return items

    def _scan_and_preview(self):
        src = self.source_dir_var.get()
        if not os.path.exists(src):
            self.status_var.set(f"Directory not found: {src}")
            return

        out_name = self.output_name_var.get().strip()
        out_full = os.path.normpath(os.path.join(src, out_name))
        arch_name = self.archive_name_var.get().strip()
        arch_full = os.path.normpath(os.path.join(src, arch_name)) if arch_name else None

        # Find images in source (excluding output and archive folders)
        image_files = []
        for pat in ["*.jpg", "*.jpeg", "*.png"]:
            for f in glob.glob(os.path.join(src, pat)):
                if os.path.isfile(f):
                    dir_norm = os.path.normpath(os.path.dirname(f))
                    if dir_norm != out_full and (not arch_full or dir_norm != arch_full):
                        image_files.append(f)

        image_files.sort(key=lambda f: os.stat(f).st_mtime)

        skipped_set = self._get_skipped_set()
        valid_prompts = [(ts, text) for (ts, text) in self.prompts_list if ts not in skipped_set]
        if hasattr(self, "prompts_btn"):
            self.prompts_btn.configure(text=f"📝 Input / Paste Prompts ({len(self.prompts_list)})")

        self.mapped_items = []
        for idx, (img_path, (ts_raw, prompt_text)) in enumerate(zip(image_files, valid_prompts)):
            ts_clean = ts_raw.strip("[]").replace(":", "-")
            prefix = f"[{ts_clean}] "
            new_filename = sanitize_filename(prompt_text, prefix, ext=os.path.splitext(img_path)[1])
            mtime = os.stat(img_path).st_mtime
            dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

            self.mapped_items.append({
                "index": idx + 1,
                "timestamp": ts_raw,
                "download_time": dt_str,
                "orig_path": img_path,
                "orig_filename": os.path.basename(img_path),
                "new_filename": new_filename,
                "prompt_text": prompt_text
            })

        # Update Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.mapped_items:
            self.tree.insert(
                "",
                "end",
                values=(
                    item["index"],
                    item["timestamp"],
                    item["download_time"],
                    item["orig_filename"],
                    item["new_filename"]
                )
            )

        match_count = len(self.mapped_items)
        img_count = len(image_files)
        prompt_count = len(valid_prompts)
        self.count_badge.configure(text=f"{match_count} Matched ({img_count} imgs / {prompt_count} prompts)")
        if img_count == 0:
            self.status_var.set("Main folder is clean! Ready to receive new images for another process.")
        else:
            self.status_var.set(f"Scanned {img_count} images. Successfully aligned {match_count} with prompt timeline.")

        if self.mapped_items:
            first_id = self.tree.get_children()[0]
            self.tree.selection_set(first_id)
            self._display_item_details(self.mapped_items[0])
        else:
            self.thumb_label.configure(image="", text="Main folder is clean.\nReady for new images.")
            self.lbl_sel_ts.configure(text="Timestamp: -")
            self.lbl_sel_time.configure(text="Created: -")
            self.lbl_sel_file.configure(text="File: -")
            self.prompt_text_box.configure(state="normal")
            self.prompt_text_box.delete("1.0", "end")
            self.prompt_text_box.configure(state="disabled")

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "values")[0]) - 1
        if 0 <= idx < len(self.mapped_items):
            self._display_item_details(self.mapped_items[idx])

    def _display_item_details(self, item):
        self.lbl_sel_ts.configure(text=f"Timestamp: {item['timestamp']}")
        self.lbl_sel_time.configure(text=f"Created: {item['download_time']}")
        self.lbl_sel_file.configure(text=f"File: {item['orig_filename']}")

        self.prompt_text_box.configure(state="normal")
        self.prompt_text_box.delete("1.0", "end")
        self.prompt_text_box.insert("1.0", item["prompt_text"])
        self.prompt_text_box.configure(state="disabled")

        # Load Thumbnail (with fallback to archive or output dir)
        try:
            path_to_open = item["orig_path"]
            if not os.path.exists(path_to_open):
                arch_name = self.archive_name_var.get().strip()
                arch_path = os.path.join(self.source_dir_var.get(), arch_name, item["orig_filename"])
                out_path = os.path.join(self.source_dir_var.get(), self.output_name_var.get().strip(), item["new_filename"])
                if os.path.exists(arch_path):
                    path_to_open = arch_path
                elif os.path.exists(out_path):
                    path_to_open = out_path

            pil_img = Image.open(path_to_open)
            pil_img.thumbnail((300, 160))
            self.current_thumbnail = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            self.thumb_label.configure(image=self.current_thumbnail, text="")
        except Exception as e:
            self.thumb_label.configure(image="", text=f"Error previewing: {e}")

    def _start_organization(self):
        if self.is_processing:
            return
        if not self.mapped_items:
            messagebox.showwarning("No Items", "No matched images to organize. Please check the source folder.")
            return

        action = self.action_var.get()
        arch_name = self.archive_name_var.get().strip()
        do_archive = self.archive_enabled_var.get() and bool(arch_name)
        
        detail_msg = f"Are you sure you want to {action.upper()} {len(self.mapped_items)} images into '{self.output_name_var.get()}'?"
        if do_archive and action == "copy":
            detail_msg += f"\n\nOriginal images will be moved to '{arch_name}', cleaning the main folder for new downloads."

        confirm = messagebox.askyesno(
            "Confirm Organization",
            detail_msg
        )
        if not confirm:
            return

        self.is_processing = True
        self.run_btn.configure(state="disabled", text="⏳ Processing...")
        self.scan_btn.configure(state="disabled")
        self.progress_bar.set(0)

        threading.Thread(target=self._process_worker, daemon=True).start()

    def _process_worker(self):
        src = self.source_dir_var.get()
        out_name = self.output_name_var.get().strip()
        out_dir = os.path.join(src, out_name)
        arch_name = self.archive_name_var.get().strip()
        arch_dir = os.path.join(src, arch_name) if arch_name else None
        do_archive = self.archive_enabled_var.get() and bool(arch_dir)
        action = self.action_var.get()

        os.makedirs(out_dir, exist_ok=True)
        if do_archive:
            os.makedirs(arch_dir, exist_ok=True)

        total = len(self.mapped_items)
        mapping_records = []

        for i, item in enumerate(self.mapped_items):
            dest_path = os.path.join(out_dir, item["new_filename"])
            try:
                if action == "move":
                    shutil.move(item["orig_path"], dest_path)
                else:
                    shutil.copy2(item["orig_path"], dest_path)
                    if do_archive:
                        shutil.move(item["orig_path"], os.path.join(arch_dir, item["orig_filename"]))

                mapping_records.append({
                    "index": item["index"],
                    "timestamp": item["timestamp"],
                    "download_time": item["download_time"],
                    "original_filename": item["orig_filename"],
                    "new_filename": item["new_filename"],
                    "prompt_text": item["prompt_text"],
                    "archived_location": os.path.join(arch_name, item["orig_filename"]) if do_archive else ""
                })
            except Exception as e:
                print(f"Error on {item['orig_filename']}: {e}")

            progress = (i + 1) / total
            self.after(0, self._update_progress, progress, f"Organizing: {i+1}/{total} - {item['new_filename']}")

        # Save manifests
        try:
            csv_path = os.path.join(out_dir, "mapping_manifest.csv")
            with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "index", "timestamp", "download_time",
                    "original_filename", "new_filename", "prompt_text", "archived_location"
                ])
                writer.writeheader()
                writer.writerows(mapping_records)

            json_path = os.path.join(out_dir, "mapping_manifest.json")
            with open(json_path, mode="w", encoding="utf-8") as f:
                json.dump(mapping_records, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Manifest write error:", e)

        self.after(0, self._on_process_complete, total, out_dir, arch_dir, do_archive)

    def _update_progress(self, progress, status_msg):
        self.progress_bar.set(progress)
        self.status_var.set(status_msg)

    def _on_process_complete(self, total, out_dir, arch_dir, did_archive):
        self.is_processing = False
        self.run_btn.configure(state="normal", text="▶ Run Organization")
        self.scan_btn.configure(state="normal")
        
        msg = f"Successfully organized {total} images!\n\nSaved in:\n{out_dir}"
        if did_archive and arch_dir:
            msg += f"\n\nOriginal images archived to:\n{arch_dir}\n\nMain folder is now clean to welcome new images!"
            self.status_var.set(f"Completed! {total} organized and originals archived. Main folder is clean.")
        else:
            self.status_var.set(f"Completed! {total} images organized into: {out_dir}")
            
        messagebox.showinfo("Success", msg)
        self._scan_and_preview()

    def _open_output_dir(self):
        src = self.source_dir_var.get()
        out_name = self.output_name_var.get().strip()
        out_dir = os.path.join(src, out_name)
        if os.path.exists(out_dir):
            os.startfile(out_dir)
        else:
            messagebox.showinfo("Folder Not Found", f"Output folder has not been created yet:\n{out_dir}")

    def _open_originals_dir(self):
        src = self.source_dir_var.get()
        arch_name = self.archive_name_var.get().strip()
        arch_dir = os.path.join(src, arch_name)
        if os.path.exists(arch_dir):
            os.startfile(arch_dir)
        else:
            messagebox.showinfo("Folder Not Found", f"Originals archive folder has not been created yet:\n{arch_dir}")


def main():
    app = ImageOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
