import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font

# Votre array initial
names = ["signals/hyper.wav", "signals/hypo.wav", 
         "signals/hyper_bébé_0DB.wav", "signals/hyper_bébé_10DB.wav", "signals/hyper_bébé_20DB.wav","signals/hyper_bébé_30DB.wav",
         "signals/hyper_chien_0DB.wav", "signals/hyper_chien_10DB.wav", "signals/hyper_chien_20DB.wav","signals/hyper_chien_30DB.wav",
         "signals/hyper_discussion_0DB.wav", "signals/hyper_discussion_10DB.wav", "signals/hyper_discussion_20DB.wav","signals/hyper_discussion_30DB.wav",
         "signals/hyper_moustique_0DB.wav", "signals/hyper_moustique_10DB.wav", "signals/hyper_moustique_20DB.wav","signals/hyper_moustique_30DB.wav",
         "signals/hyper_vache_0DB.wav", "signals/hyper_vache_10DB.wav", "signals/hyper_vache_20DB.wav","signals/hyper_vache_30DB.wav",
         "signals/hypo_bébé_0DB.wav", "signals/hypo_bébé_10DB.wav", "signals/hypo_bébé_20DB.wav","signals/hypo_bébé_30DB.wav",
         "signals/hypo_chien_0DB.wav", "signals/hypo_chien_10DB.wav", "signals/hypo_chien_20DB.wav","signals/hypo_chien_30DB.wav",
         "signals/hypo_discussion_0DB.wav", "signals/hypo_discussion_10DB.wav", "signals/hypo_discussion_20DB.wav","signals/hypo_discussion_30DB.wav",
         "signals/hypo_moustique_0DB.wav", "signals/hypo_moustique_10DB.wav", "signals/hypo_moustique_20DB.wav","signals/hypo_moustique_30DB.wav",
         "signals/hypo_vache_0DB.wav", "signals/hypo_vache_10DB.wav", "signals/hypo_vache_20DB.wav","signals/hypo_vache_30DB.wav"]


# Création ou ouverture d'un fichier Excel
file_name = "output.xlsx"
wb = openpyxl.Workbook()
sheet = wb.active
sheet.title = "Statuts"

# Insertion des données dans les colonnes A et B
sheet["A1"] = "Name"
sheet["B1"] = "Status"
sheet["A1"].font = Font(bold=True)
sheet["B1"].font = Font(bold=True)

for i, name in enumerate(names, start=2):
    sheet[f"A{i}"] = name
    sheet[f"B{i}"] = "OK"  # Statut par défaut

# Ajout d'un tableau des comptages
sheet["D1"] = "Status"
sheet["E1"] = "Count"
sheet["D1"].font = Font(bold=True)
sheet["E1"].font = Font(bold=True)

statuses = {"OK": len(names), "NOK": 0}
for i, (status, count) in enumerate(statuses.items(), start=2):
    sheet[f"D{i}"] = status
    sheet[f"E{i}"] = count

# Création d'un graphique à barres
chart = BarChart()
chart.title = "Statut des entrées"
chart.x_axis.title = "Status"
chart.y_axis.title = "Count"
data = Reference(sheet, min_col=5, min_row=1, max_row=len(statuses) + 1, max_col=5)
cats = Reference(sheet, min_col=4, min_row=2, max_row=len(statuses) + 1)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4

# Positionner le graphique dans la feuille
sheet.add_chart(chart, "G2")

# Sauvegarde du fichier Excel
wb.save(file_name)
print(f"Données et graphique ajoutés au fichier Excel: {file_name}")
