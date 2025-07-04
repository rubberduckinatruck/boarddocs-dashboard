import os

folder = r'C:\Users\gturnbull\Desktop\AGENDA_BoardDocs\Cleaned_Yearly_Jsons'

for filename in os.listdir(folder):
    if filename.endswith('.json') and not filename.endswith('_cleaned.json'):
        base, ext = os.path.splitext(filename)
        newname = f"{base}_cleaned{ext}"
        os.rename(
            os.path.join(folder, filename),
            os.path.join(folder, newname)
        )
        print(f"Renamed: {filename}  →  {newname}")