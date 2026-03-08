import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
from PIL import Image, ImageTk

# ── THEME ──────────────────────────────────────────────────────────────────
BG_DARK   = "#2D2D30"
BG_PANEL  = "#1E1E1E"
FG_MAIN   = "#FFFFFF"
FG_GRAY   = "#808080"
ACCENT    = "#007ACC"
BTN_GREEN = "#3C8527"
BTN_RES   = "#4A4A4F"
BTN_RES_ON= "#CC7A00"

# Base canvas sizes in 16x tile units (width_tiles, height_tiles)
# Multiply by tile_px at build time to get pixel size
CANVAS_TILES = {
    "terrain":   (16, 32),
    "items":     (16, 16),
    "particles": (8,  8),
}

_preview_img = None

projects = {
    "terrain":   {"json_path": "", "layout": [], "final_map": {}},
    "items":     {"json_path": "", "layout": [], "final_map": {}},
    "particles": {"json_path": "", "layout": [], "final_map": {}},
}
source_dir    = {"v": ""}
current_scale = {"v": 1}   # 1=16x  2=32x  4=64x

TAB_ORDER = ["terrain", "items", "particles"]

# ── ROOT ───────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Texture Manager v5.5")
root.geometry("1000x800")
root.minsize(800, 600)
root.configure(bg=BG_DARK)

# ── TTK STYLES ─────────────────────────────────────────────────────────────
style = ttk.Style()
style.theme_use("default")
style.configure("Dark.Treeview",
                background=BG_PANEL, foreground=FG_MAIN,
                fieldbackground=BG_PANEL, rowheight=22,
                font=("Segoe UI", 9))
style.configure("Dark.Treeview.Heading",
                background="#3C3C3C", foreground=FG_MAIN,
                font=("Segoe UI", 9, "bold"), relief="flat")
style.map("Dark.Treeview",
          background=[("selected", ACCENT)],
          foreground=[("selected", FG_MAIN)])
style.configure("Dark.TNotebook",
                background=BG_DARK, borderwidth=0, tabmargins=0)
style.configure("Dark.TNotebook.Tab",
                background="#3C3C3C", foreground=FG_GRAY,
                padding=[18, 7], font=("Segoe UI", 9, "bold"))
style.map("Dark.TNotebook.Tab",
          background=[("selected", ACCENT)],
          foreground=[("selected", FG_MAIN)])

# ═══════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════
top_bar = tk.Frame(root, bg=BG_PANEL, height=46)
top_bar.pack(side="top", fill="x")
top_bar.pack_propagate(False)

def pick_library():
    d = filedialog.askdirectory(title="Select Texture Library Folder")
    if d:
        source_dir["v"] = d
        btn_lib.config(text=f"Library: {Path(d).name}")

btn_lib = tk.Button(top_bar, text="1. SELECT LIBRARY",
                    bg="#3C3C3C", fg=FG_MAIN,
                    activebackground="#505050", activeforeground=FG_MAIN,
                    relief="flat", font=("Segoe UI", 9, "bold"),
                    command=pick_library)
btn_lib.pack(side="left", padx=(8, 6), pady=7, ipady=5, ipadx=10)

json_btns = {}
for ptype in TAB_ORDER:
    def make_json_cmd(pt):
        def cmd():
            f = filedialog.askopenfilename(
                title=f"Select {pt.upper()} JSON",
                filetypes=[("JSON Files", "*.json")])
            if f:
                with open(f, "r", encoding="utf-8") as fh:
                    projects[pt]["layout"] = json.load(fh)
                projects[pt]["json_path"] = f
                projects[pt]["final_map"] = {}
                json_btns[pt].config(
                    text=f"{pt.upper()} JSON: {Path(f).name}",
                    fg="#90EE90")
                refresh_list(pt)
        return cmd
    b = tk.Button(top_bar,
                  text=f"{ptype.upper()} JSON: ---",
                  bg="#3C3C3C", fg=FG_GRAY,
                  activebackground="#505050", activeforeground=FG_MAIN,
                  relief="flat", font=("Segoe UI", 9),
                  command=make_json_cmd(ptype))
    b.pack(side="left", padx=4, pady=7, ipady=5, ipadx=8)
    json_btns[ptype] = b

tk.Frame(top_bar, bg="#555555", width=2).pack(
    side="left", fill="y", pady=8, padx=6)

res_btns = {}

def set_resolution(scale):
    current_scale["v"] = scale
    labels = {1: "16x", 2: "32x", 4: "64x"}
    for s, btn in res_btns.items():
        if s == scale:
            btn.config(bg=BTN_RES_ON, fg=FG_MAIN, relief="sunken")
        else:
            btn.config(bg=BTN_RES, fg=FG_GRAY, relief="flat")
    root.title(f"Texture Manager v5.5  [{labels[scale]}]")

for scale, label in [(1, "16x"), (2, "32x"), (4, "64x")]:
    def make_res_cmd(s):
        return lambda: set_resolution(s)
    b = tk.Button(top_bar, text=label,
                  bg=BTN_RES, fg=FG_GRAY,
                  activebackground="#666666", activeforeground=FG_MAIN,
                  relief="flat", font=("Segoe UI", 9, "bold"), width=4,
                  command=make_res_cmd(scale))
    b.pack(side="left", padx=2, pady=7, ipady=5)
    res_btns[scale] = b

set_resolution(1)

# ═══════════════════════════════════════════════════════════════════════════
# LOAD TILE
# Crops to a square first frame (handles animated strips of any height),
# then resizes to exactly tile_px × tile_px using nearest neighbour.
# ═══════════════════════════════════════════════════════════════════════════
def load_tile(fpath, tile_px):
    img = Image.open(fpath).convert("RGBA")
    w, h = img.size

    # Determine the native tile size: smallest of w and h
    # (animated strips are always taller than wide)
    native = min(w, h)

    # Crop to first frame (top-left native×native square)
    if w != native or h != native:
        img = img.crop((0, 0, native, native))

    # Scale to target tile size
    if img.size != (tile_px, tile_px):
        img = img.resize((tile_px, tile_px), Image.NEAREST)

    return img


# ═══════════════════════════════════════════════════════════════════════════
# NOTEBOOK TABS
# ═══════════════════════════════════════════════════════════════════════════
notebook = ttk.Notebook(root, style="Dark.TNotebook")
notebook.pack(side="top", fill="both", expand=True, padx=10, pady=(6, 0))

trees    = {}
previews = {}

for ptype in TAB_ORDER:
    tab = tk.Frame(notebook, bg=BG_DARK)
    notebook.add(tab, text=f"  {ptype.upper()}  ")

    sv = tk.StringVar()
    se = tk.Entry(tab, textvariable=sv,
                  bg=BG_PANEL, fg=FG_MAIN, insertbackground=FG_MAIN,
                  relief="flat", font=("Segoe UI", 10))
    se.pack(side="top", fill="x", padx=0, pady=(0, 4), ipady=4)
    projects[ptype]["search_var"] = sv
    sv.trace_add("write", lambda *_, pt=ptype: refresh_list(pt))

    pane = tk.PanedWindow(tab, orient=tk.HORIZONTAL,
                          bg=BG_DARK, sashwidth=5, sashrelief="flat")
    pane.pack(fill="both", expand=True)

    lf = tk.Frame(pane, bg=BG_PANEL)
    pane.add(lf, width=620, minsize=300)

    tree = ttk.Treeview(lf, columns=("block", "source"),
                        show="headings", style="Dark.Treeview",
                        selectmode="browse")
    tree.heading("block",  text="BLOCK TYPE")
    tree.heading("source", text="SOURCE FILE")
    tree.column("block",  width=250, anchor="w")
    tree.column("source", width=350, anchor="w")
    vsb = ttk.Scrollbar(lf, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    trees[ptype] = tree

    rf = tk.Frame(pane, bg=BG_DARK)
    pane.add(rf, minsize=200)

    pc = tk.Canvas(rf, bg="black", highlightthickness=0)
    pc.place(x=10, y=10, relwidth=1.0, width=-20, height=310)
    previews[ptype] = pc

    def make_auto(pt):
        def do_auto():
            if not source_dir["v"]:
                messagebox.showwarning("No Library",
                    "Please select a library folder first.")
                return
            png_files = {}
            for r, _, files in os.walk(source_dir["v"]):
                for f in files:
                    if f.lower().endswith(".png"):
                        base = Path(f).stem
                        if base not in png_files:
                            png_files[base] = os.path.join(r, f)
            matched = 0
            for i, obj in enumerate(projects[pt]["layout"]):
                name = obj.get("Name") or obj.get("n", "")
                if name in png_files:
                    projects[pt]["final_map"][i] = png_files[name]
                    matched += 1
            refresh_list(pt)
            messagebox.showinfo("Auto-Sync Complete",
                f"Matched {matched} of {len(projects[pt]['layout'])} entries.")
        return do_auto

    tk.Button(rf, text="AUTO-SYNC FROM LIBRARY",
              bg=ACCENT, fg=FG_MAIN,
              activebackground="#005FA3", activeforeground=FG_MAIN,
              relief="flat", font=("Segoe UI", 10, "bold"),
              command=make_auto(ptype)).place(
        x=10, y=328, relwidth=1.0, width=-20, height=52)

    def make_sel(pt):
        def on_sel(event):
            global _preview_img
            sel = trees[pt].selection()
            if not sel:
                return
            idx = int(sel[0])
            previews[pt].delete("all")
            if idx not in projects[pt]["final_map"]:
                return
            try:
                img = load_tile(projects[pt]["final_map"][idx], 16)
                cw  = previews[pt].winfo_width()  or 310
                ch  = previews[pt].winfo_height() or 310
                sc  = max(1, min(cw // img.width, ch // img.height))
                img = img.resize(
                    (img.width * sc, img.height * sc), Image.NEAREST)
                _preview_img = ImageTk.PhotoImage(img)
                ox = (cw - img.width)  // 2
                oy = (ch - img.height) // 2
                previews[pt].create_image(ox, oy, anchor="nw",
                                          image=_preview_img)
            except Exception:
                pass
        return on_sel

    tree.bind("<<TreeviewSelect>>", make_sel(ptype))

    def make_dbl(pt):
        def on_dbl(event):
            sel = trees[pt].selection()
            if not sel:
                return
            idx  = int(sel[0])
            path = filedialog.askopenfilename(
                title="Select PNG",
                filetypes=[("PNG Files", "*.png")])
            if path:
                projects[pt]["final_map"][idx] = path
                refresh_list(pt)
                trees[pt].selection_set(str(idx))
        return on_dbl

    tree.bind("<Double-1>", make_dbl(ptype))

# ═══════════════════════════════════════════════════════════════════════════
# REFRESH LIST
# ═══════════════════════════════════════════════════════════════════════════
def refresh_list(ptype=None):
    if ptype is None:
        ptype = TAB_ORDER[notebook.index(notebook.select())]
    tree = trees[ptype]
    proj = projects[ptype]
    filt = proj["search_var"].get().lower()
    tree.delete(*tree.get_children())
    for i, obj in enumerate(proj["layout"]):
        display = (obj.get("DisplayName") or
                   obj.get("n") or
                   obj.get("Name", ""))
        if filt and filt not in display.lower():
            continue
        fname = (os.path.basename(proj["final_map"][i])
                 if i in proj["final_map"] else "---")
        iid = tree.insert("", "end", iid=str(i), values=(display, fname))
        if fname == "---":
            tree.item(iid, tags=("gray",))
    tree.tag_configure("gray", foreground=FG_GRAY)

notebook.bind("<<NotebookTabChanged>>", lambda *_: refresh_list())

# ═══════════════════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════════════════
def do_build():
    ptype   = TAB_ORDER[notebook.index(notebook.select())]
    proj    = projects[ptype]
    scale   = current_scale["v"]
    tile_px = 16 * scale          # e.g. 32 for 32x

    if not proj["json_path"]:
        messagebox.showwarning("No JSON",
            f"Please load a {ptype.upper()} JSON first.")
        return

    cols, rows = CANVAS_TILES[ptype]
    cw = cols * tile_px            # canvas width  in pixels
    ch = rows * tile_px            # canvas height in pixels

    canvas_img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    placed = 0
    errors = 0
    for k, fpath in proj["final_map"].items():
        if not os.path.exists(fpath):
            continue
        try:
            tile = load_tile(fpath, tile_px)
            obj  = proj["layout"][k]

            # Convert JSON coord (always 16x pixel space) → grid slot → output pixel
            json_x = int(obj.get("X", obj.get("x", 0)))
            json_y = int(obj.get("Y", obj.get("y", 0)))
            col    = json_x // 16   # which grid column  (0-based)
            row    = json_y // 16   # which grid row     (0-based)
            px     = col * tile_px  # output pixel X
            py     = row * tile_px  # output pixel Y

            # Use tile as its own alpha mask so transparent edges
            # never overwrite adjacent tiles
            canvas_img.paste(tile, (px, py), tile)
            placed += 1
        except Exception as e:
            errors += 1

    out_dir   = os.path.dirname(proj["json_path"])
    json_base = Path(proj["json_path"]).stem
    out_path  = os.path.join(out_dir, f"{json_base}.png")
    canvas_img.save(out_path)

    if ptype == "terrain":
        canvas_img.resize((cw // 2, ch // 2), Image.NEAREST).save(
            os.path.join(out_dir, "terrainMipMapLevel2.png"))
        canvas_img.resize((cw // 4, ch // 4), Image.NEAREST).save(
            os.path.join(out_dir, "terrainMipMapLevel3.png"))

    res_label = {1: "16x", 2: "32x", 4: "64x"}[scale]
    msg = (f"Resolution: {res_label}\n"
           f"Canvas: {cw}×{ch}\n"
           f"Tiles placed: {placed}")
    if errors:
        msg += f"\nErrors skipped: {errors}"
    messagebox.showinfo("Build Complete", f"{msg}\n\nSaved to:\n{out_path}")

# ── BOTTOM BUILD BAR ───────────────────────────────────────────────────────
bottom = tk.Frame(root, bg=BG_DARK, height=70)
bottom.pack(side="bottom", fill="x", padx=10, pady=(0, 8))
bottom.pack_propagate(False)

tk.Button(bottom, text="BUILD ASSETS",
          bg=BTN_GREEN, fg=FG_MAIN,
          activebackground="#2E6B1A", activeforeground=FG_MAIN,
          relief="flat", font=("Segoe UI", 12, "bold"),
          command=do_build).pack(fill="both", expand=True)

root.mainloop()
