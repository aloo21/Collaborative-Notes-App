import customtkinter as ctk
from tkinter import messagebox


class DeletePage(ctk.CTkToplevel):
    def __init__(self, parent, notes, save_callback, refresh_callback):
        super().__init__(parent)

        self.title("حذف الملاحظات")
        self.geometry("480x600")
        self.notes = notes
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback

        title_lbl = ctk.CTkLabel(self, text="اختر الملاحظة التي تريدين حذفها", font=("Arial", 22, "bold"))
        title_lbl.pack(pady=15)

        self.container = ctk.CTkScrollableFrame(self, width=450, height=500)
        self.container.pack(pady=10, padx=10)

        self.display_notes()

    # ---------------------------------------------------
    def display_notes(self):
        """عرض كل الملاحظات داخل الصفحة"""
        for widget in self.container.winfo_children():
            widget.destroy()

        for index, note in enumerate(self.notes):
            row = ctk.CTkFrame(self.container)
            row.pack(fill="x", pady=7, padx=10)

            title_lbl = ctk.CTkLabel(row, text=note["title"], font=("Arial", 18))
            title_lbl.pack(side="left", padx=10)

            delete_btn = ctk.CTkButton(
                row,
                text="حذف",
                width=80,
                fg_color="#D32F2F",
                text_color="white",
                hover_color="#B71C1C",
                command=lambda idx=index: self.delete_note(idx)
            )
            delete_btn.pack(side="right", padx=10)

    # ---------------------------------------------------
    def delete_note(self, index):
        """حذف الملاحظة عند الضغط على زر الحذف"""

        confirm = messagebox.askyesno("تأكيد", "هل تريدين حذف هذه الملاحظة؟")

        if confirm:
            del self.notes[index]          # احذف من القائمة
            self.save_callback(self.notes) # احفظ في JSON
            self.refresh_callback()        # تحدّث الصفحة الرئيسية
            messagebox.showinfo("تم", "تم حذف الملاحظة بنجاح.")

            self.display_notes()  # إعادة تحديث الصفحة
