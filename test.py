from src.bim.report_pdf.school_report_pdf import DataProject, SchoolReportePDF

data_project : DataProject = {
    "name_project" : "Nuevo Proyecto",
    "niveles" : ["Primaria", "Secundaria"]
}


pdf = SchoolReportePDF(data_project=data_project, output_path="reporte.pdf")

pdf.portada()
pdf.info_project()
pdf.add_svgs_from_folder(folder_path="temp_9fd3416ec249")

pdf.add_area_summary_table([
    ["Aula primaria", "60 m²"],
    ["Aula secundaria", "60 m²"],
    ["Biblioteca", "90 m²"],
    ["SUM", "300 m²"],
])

pdf.add_general_area_table({
    "area_pabellones": "500 m²",
    "pisos_pabellones": "3",
    "area_pasadizos": "120 m²",
    "area_techada": "800 m²",
    "area_libre": "700 m²",
})

pdf.save()
