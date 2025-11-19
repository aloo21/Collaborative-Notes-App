# app_ctk.py
import json
import os
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

# ------------ إعداد CustomTkinter ------------
ctk.set_appearance_mode("Light")  # "Dark" ممكن لاحقاً للتبديل
ctk.set_default_color_theme("blue")  # يؤثر في الأزرار والألوان الافتراضية

NOTES_FILE = "notes.json"

PALETTE = {
    "bg": "#F6F7FB",
    "card": "#FFFFFF",
    "accent": "#7ED6DF",    # تيفاني pastel
    "accent2": "#C39BD3",   # بنفسجي فاتح
    "muted": "#8E9AAF",
    "delete": "#FF6B6B",
}

# ------------ JSON helpers مع معالجة الأخطاء ------------
def init_notes_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)

# ------------ نافذة التفاصيل المنبثقة ------------
def open_note_modal(master, note, refresh_callback=None):
    top = ctk.CTkToplevel(master)
    top.title(note.get("title", "ملاحظة"))
    top.geometry("420x320")
    top.configure(fg_color=PALETTE["bg"])

    title_lbl = ctk.CTkLabel(top, text=note["title"], font=ctk.CTkFont(size=16, weight="bold"),
                             anchor="e", justify="right")
    title_lbl.pack(fill="x", pady=(12,6), padx=12)

    date_lbl = ctk.CTkLabel(top, text=note["date"], font=ctk.CTkFont(size=11), fg_color=None, anchor="e")
    date_lbl.pack(fill="x", padx=12)

    body_txt = ctk.CTkTextbox(top, wrap="word", height=12)
    body_txt.insert("0.0", note["body"])
    body_txt.configure(state="disabled", fg_color=PALETTE["card"], corner_radius=8)
    body_txt.pack(fill="both", expand=True, padx=12, pady=12)

# ------------ تطبيق الواجهة الرئيسية ------------
class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("تطبيق الملاحظات — Pastel")
        self.geometry("760x560")
        self.minsize(600, 450)
        self.configure(fg_color=PALETTE["bg"])

        init_notes_file()
        self.notes = load_notes()
        self.filtered_notes = self.notes.copy()

        self._build_ui()
        self.refresh_notes_display()

    def _build_ui(self):
        # رأس التطبيق
        header = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        header.pack(fill="x", padx=16, pady=(12,8))

        title = ctk.CTkLabel(header, text="تطبيق الملاحظات", font=ctk.CTkFont(size=20, weight="bold"),
                             anchor="e")
        title.pack(side="right")

        subtitle = ctk.CTkLabel(header, text="واجهة Pastel بتأثير Hover وCards", font=ctk.CTkFont(size=11),
                                fg_color=None, text_color=PALETTE["muted"], anchor="e")
        subtitle.pack(side="right", padx=(0,12))

        # المنطقة الرئيسية: قسم الإدخال + قسم العرض
        main_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # ----- جهة اليمين: إدخال ملاحظة -----
        right_panel = ctk.CTkFrame(main_frame, fg_color=PALETTE["bg"], corner_radius=0)
        right_panel.pack(side="right", fill="y", padx=(0,12), pady=8)

        lbl_title = ctk.CTkLabel(right_panel, text="عنوان الملاحظة:", anchor="e")
        lbl_title.pack(anchor="e", pady=(6,2), padx=4)
        self.entry_title = ctk.CTkEntry(right_panel, width=320, placeholder_text="ضع عنوانًا مختصرًا")
        self.entry_title.pack(padx=4, pady=(0,8))

        lbl_body = ctk.CTkLabel(right_panel, text="نص الملاحظة:", anchor="e")
        lbl_body.pack(anchor="e", pady=(6,2), padx=4)
        self.text_body = ctk.CTkTextbox(right_panel, width=320, height=10)
        self.text_body.pack(padx=4, pady=(0,8))

        # زر الإضافة مع تأثير hover بسيط (تغيير اللون وحجم الخط)
        self.add_btn = ctk.CTkButton(right_panel, text="إضافة الملاحظة", command=self.on_add_click,
                                     width=200, height=40, corner_radius=12,
                                     fg_color=PALETTE["accent"], text_color="white")
        self.add_btn.pack(pady=8)

        # ربط hover (تكبير طفيف وتغيير لون)
        self.add_btn.bind("<Enter>", self._on_add_hover)
        self.add_btn.bind("<Leave>", self._on_add_leave)

        # زر تبديل الLight/Dark (اختياري)
        self.mode_switch = ctk.CTkSwitch(right_panel, text="Dark Mode", command=self.toggle_mode)
        self.mode_switch.pack(pady=(10,0))

        # ----- جهة اليسار: عرض الملاحظات (Scrollable cards) -----
        left_panel = ctk.CTkFrame(main_frame, fg_color=PALETTE["bg"], corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(12,0), pady=8)

        notes_label = ctk.CTkLabel(left_panel, text="جميع الملاحظات", font=ctk.CTkFont(size=14, weight="bold"),
                                   anchor="w")
        notes_label.pack(fill="x", padx=6, pady=(2,6))

        search_frame = ctk.CTkFrame(left_panel, fg_color=PALETTE["bg"])
        search_frame.pack(fill="x", padx=6, pady=(0, 8))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 ابحث في الملاحظات...",
            width=300
        )
        self.search_entry.pack(side="right", padx=4)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # زر مسح البحث
        clear_btn = ctk.CTkButton(
            search_frame, text="مسح",
            width=60, command=self.clear_search,
            fg_color=PALETTE["muted"]
        )
        clear_btn.pack(side="right", padx=4)

        # شريط تمرير مع إطار قابل للتمرير

        self.scroll_frame = ctk.CTkScrollableFrame(left_panel, fg_color=PALETTE["bg"])
        self.scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)

    # ---------- فعّاليات الواجهة ----------
    def _on_add_hover(self, event):
        # تغيير لون وحجم الخط كأنيمشن بسيط
        event.widget.configure(fg_color=PALETTE["accent2"])
        event.widget.configure(font=ctk.CTkFont(size=12, weight="bold"))

    def _on_add_leave(self, event):
        event.widget.configure(fg_color=PALETTE["accent"])
        event.widget.configure(font=ctk.CTkFont(size=11))

    def toggle_mode(self):
        # تبديل أوتوماتيكي بين Light و Dark
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Dark" if current == "Light" else "Light")

    def on_add_click(self):
        title = self.entry_title.get().strip()
        body = self.text_body.get("0.0", "end").strip()

        if not title or not body:
            messagebox.showwarning("خطأ", "الرجاء إدخال عنوان ونص الملاحظة.")
            return

        note = {
            "title": title,
            "body": body,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.notes.append(note)
        save_notes(self.notes)

        # مؤثر بسيط: مسح الحقول ثم عرض رسالة صغيرة ثم تحديث العرض
        self.entry_title.delete(0, "end")
        self.text_body.delete("0.0", "end")

        # تأكيد بصري صغير
        self.add_btn.configure(text="تمت الإضافة ✓")
        self.after(900, lambda: self.add_btn.configure(text="إضافة الملاحظة"))
        self.filtered_notes = self.notes.copy()
        self.refresh_notes_display()

    def on_search(self, event=None):
        query = self.search_entry.get().strip().lower()

        if not query:
            self.filtered_notes = self.notes.copy()
        else:
            self.filtered_notes = [
                note for note in self.notes
                if query in note["title"].lower() or query in note["body"].lower()
            ]

        self.refresh_notes_display()

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.filtered_notes = self.notes.copy()
        self.refresh_notes_display()

    def refresh_notes_display(self):
        print(f"🔍 تحديث العرض... عدد الملاحظات: {len(self.filtered_notes)}")

        # تنظيف كل شيء في scroll_frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # إذا لم توجد ملاحظات
        if not self.filtered_notes:
            msg = "لا توجد ملاحظات حتى الآن." if not self.notes else "لا توجد نتائج للبحث."
            empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text=msg,
                text_color=PALETTE["muted"],
                font=ctk.CTkFont(size=13)
            )
            empty_label.pack(pady=20)
            print("⚠ لا توجد ملاحظات لعرضها")
            return

        # عرض الملاحظات (الأحدث أولاً)
        print(f"✅ سيتم عرض {len(self.filtered_notes)} ملاحظة")
        for idx, note in enumerate(reversed(self.filtered_notes)):
            try:
                original_index = self.notes.index(note)
                print(f"  → إنشاء بطاقة: {note['title'][:20]}...")
                self._create_card(self.scroll_frame, note, original_index)
            except Exception as e:
                print(f"❌ خطأ في إنشاء البطاقة {idx}: {e}")

        # تحديث العرض
        self.scroll_frame.update_idletasks()
        print("✅ تم تحديث العرض بنجاح")

    def _create_card(self, parent, note, index):
        card = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=10, height=100)
        card.pack(fill="x", pady=8, padx=6)

        # إطار المحتوى
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=12, pady=10)

        # العنوان
        title_lbl = ctk.CTkLabel(
            content_frame, text=note["title"],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="e"
        )
        title_lbl.pack(anchor="e", pady=(0, 2))

        # التاريخ
        date_lbl = ctk.CTkLabel(
            content_frame, text=note["date"],
            font=ctk.CTkFont(size=10),
            text_color=PALETTE["muted"],
            anchor="e"
        )
        date_lbl.pack(anchor="e", pady=(0, 6))

        # نص مختصر
        snippet = note["body"]
        if len(snippet) > 60:
            snippet = snippet[:60] + "..."

        body_lbl = ctk.CTkLabel(
            content_frame, text=snippet,
            anchor="w", wraplength=350,
            justify="right"
        )
        body_lbl.pack(anchor="e", pady=(0, 8))

        # الأزرار
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(anchor="w")

        view_btn = ctk.CTkButton(
            btn_frame, text="عرض", width=70,
            fg_color=PALETTE["accent"],
            command=lambda n=note: open_note_modal(self, n)
        )
        view_btn.pack(side="left", padx=2)


        # Hover effect
        card.bind("<Enter>", lambda e: card.configure(fg_color="#FBFBFF"))
        card.bind("<Leave>", lambda e: card.configure(fg_color=PALETTE["card"]))

# ------------ تشغيل التطبيق ------------
if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()
