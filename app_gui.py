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
    from organize_images import PROMPTS, SKIPPED_TIMESTAMPS, sanitize_filename
except ImportError:
    # Fallback if imported from another location
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from organize_images import PROMPTS, SKIPPED_TIMESTAMPS, sanitize_filename

# Set CustomTkinter theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ImageOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Prompt & Timeline Organizer")
        self.geometry("1180x750")
        self.minsize(960, 620)

        # Base directories
        default_dir = os.path.dirname(os.path.abspath(__file__))
        self.source_dir_var = tk.StringVar(value=default_dir)
        self.output_name_var = tk.StringVar(value="organized_images")
        self.action_var = tk.StringVar(value="copy")
        self.skipped_var = tk.StringVar(value="10:17, 3:20, 6:06")
        self.status_var = tk.StringVar(value="Ready. Click 'Scan & Match' to preview.")

        # Data state
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

        # 2. Controls & Configuration Card
        controls_card = ctk.CTkFrame(self, fg_color="#202024", corner_radius=10)
        controls_card.pack(fill="x", padx=16, pady=(12, 6))

        # Row 1: Source & Output
        r1 = ctk.CTkFrame(controls_card, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(r1, text="Source Folder:", width=95, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.src_entry = ctk.CTkEntry(r1, textvariable=self.source_dir_var, font=ctk.CTkFont(size=12))
        self.src_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(r1, text="Browse...", width=80, command=self._browse_source).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(r1, text="Output Folder:", width=90, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.out_entry = ctk.CTkEntry(r1, textvariable=self.output_name_var, width=170, font=ctk.CTkFont(size=12))
        self.out_entry.pack(side="left", padx=(0, 6))

        # Row 2: Mode, Skips & Action Buttons
        r2 = ctk.CTkFrame(controls_card, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(r2, text="Mode:", width=50, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.mode_seg = ctk.CTkSegmentedButton(
            r2,
            values=["Copy (Safe)", "Move"],
            command=self._on_mode_change
        )
        self.mode_seg.set("Copy (Safe)")
        self.mode_seg.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(r2, text="Skip Timestamps:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.skip_entry = ctk.CTkEntry(r2, textvariable=self.skipped_var, width=180, font=ctk.CTkFont(size=12))
        self.skip_entry.pack(side="left", padx=(6, 16))

        self.scan_btn = ctk.CTkButton(
            r2,
            text="🔄 Scan & Match",
            width=120,
            fg_color="#334155",
            hover_color="#475569",
            command=self._scan_and_preview
        )
        self.scan_btn.pack(side="left", padx=(0, 8))

        self.run_btn = ctk.CTkButton(
            r2,
            text="▶ Run Organization",
            width=160,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(weight="bold"),
            command=self._start_organization
        )
        self.run_btn.pack(side="left", padx=(0, 8))

        self.open_btn = ctk.CTkButton(
            r2,
            text="📂 Open Output",
            width=120,
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
            self._scan_and_preview()

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

        # Find images in source (excluding output folder if it exists inside source)
        image_files = []
        for pat in ["*.jpg", "*.jpeg", "*.png"]:
            for f in glob.glob(os.path.join(src, pat)):
                if os.path.isfile(f):
                    # Do not include files inside destination
                    if os.path.normpath(os.path.dirname(f)) != out_full:
                        image_files.append(f)

        image_files.sort(key=lambda f: os.stat(f).st_mtime)

        skipped_set = self._get_skipped_set()
        valid_prompts = [(ts, text) for (ts, text) in PROMPTS if ts not in skipped_set]

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
        self.status_var.set(f"Scanned {img_count} images. Successfully aligned {match_count} with prompt timeline.")

        if self.mapped_items:
            first_id = self.tree.get_children()[0]
            self.tree.selection_set(first_id)
            self._display_item_details(self.mapped_items[0])

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

        # Load Thumbnail
        try:
            pil_img = Image.open(item["orig_path"])
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
        confirm = messagebox.askyesno(
            "Confirm Organization",
            f"Are you sure you want to {action.upper()} {len(self.mapped_items)} images into '{self.output_name_var.get()}'?"
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
        action = self.action_var.get()

        os.makedirs(out_dir, exist_ok=True)
        total = len(self.mapped_items)
        mapping_records = []

        for i, item in enumerate(self.mapped_items):
            dest_path = os.path.join(out_dir, item["new_filename"])
            try:
                if action == "move":
                    shutil.move(item["orig_path"], dest_path)
                else:
                    shutil.copy2(item["orig_path"], dest_path)

                mapping_records.append({
                    "index": item["index"],
                    "timestamp": item["timestamp"],
                    "download_time": item["download_time"],
                    "original_filename": item["orig_filename"],
                    "new_filename": item["new_filename"],
                    "prompt_text": item["prompt_text"]
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
                    "original_filename", "new_filename", "prompt_text"
                ])
                writer.writeheader()
                writer.writerows(mapping_records)

            json_path = os.path.join(out_dir, "mapping_manifest.json")
            with open(json_path, mode="w", encoding="utf-8") as f:
                json.dump(mapping_records, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Manifest write error:", e)

        self.after(0, self._on_process_complete, total, out_dir)

    def _update_progress(self, progress, status_msg):
        self.progress_bar.set(progress)
        self.status_var.set(status_msg)

    def _on_process_complete(self, total, out_dir):
        self.is_processing = False
        self.run_btn.configure(state="normal", text="▶ Run Organization")
        self.scan_btn.configure(state="normal")
        self.status_var.set(f"Completed! {total} images organized into: {out_dir}")
        messagebox.showinfo("Success", f"Successfully organized {total} images!\n\nSaved in:\n{out_dir}")

    def _open_output_dir(self):
        src = self.source_dir_var.get()
        out_name = self.output_name_var.get().strip()
        out_dir = os.path.join(src, out_name)
        if os.path.exists(out_dir):
            os.startfile(out_dir)
        else:
            messagebox.showinfo("Folder Not Found", f"Output folder has not been created yet:\n{out_dir}")


def main():
    app = ImageOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
