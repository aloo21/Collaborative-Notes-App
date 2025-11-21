import json

def delete_note(note_id):
    try:
        with open("notes.json", "r", encoding="utf-8") as file:
            notes = json.load(file)

        new_notes = [note for note in notes if note["id"] != note_id]

        if len(new_notes) == len(notes):
            print("⚠️ لا توجد ملاحظة بهذا الرقم!")
            return

        with open("notes.json", "w", encoding="utf-8") as file:
            json.dump(new_notes, file, ensure_ascii=False, indent=4)

        print("✅ تم حذف الملاحظة بنجاح!")
    except FileNotFoundError:
        print("❌ ملف الملاحظات غير موجود.")
