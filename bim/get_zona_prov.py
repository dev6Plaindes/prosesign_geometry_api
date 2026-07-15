z1=[
    "casma",
    "huarmey",
    "sullana",
    "camaná",
    "mollendo",
    "chincha",
    "pisco",
    "pacasmayo",
    "trujillo",
    "chiclayo",
    "ferreñafe",
    "barranca",
    "chimbote",
    "huaral",
    "huaura",
    "lima",
    "ilo",
    "talara"
]

z2 =[
    "palpa",
    "ica",
    "nazca",
    "ascope",
    "chepén",
    "virú",
    "paita",
    "sechura",
    "piura"
]

z3 =[
    "caravelí",
    "castilla",
    "canta",
    "mariscal nieto",
    "general sánchez",
    "jorge basadre",
    "contralmirante villar"
]

z4 = [
    "asunción",
    "aija",
    "antonio raimondi",
    "carhuaz",
    "carlos fermín fitzcarrald",
    "huari",
    "corongo",
    "huaylas",
    "ocros",
    "yungay",
    "andahuaylas",
    "aymaraes",
    "arequipa",
    "condesuyos",
    "cangallo",
    "huamanga",
    "páucar del sara sara",
    "san miguel",
    "cusco",
    "paruro",
    "canchis",
    "acomayo",
    "anta",
    "calca",
    "paucartambo",
    "quispicanchi",
    "urubamba",
    "castrovirreyna",
    "churcampa",
    "huaytará",
    "acobamba",
    "huamalíes",
    "huánuco",
    "pachitea",
    "ambo",
    "tarma",
    "concepción",
    "huancayo",
    "chupaca",
    "jauja",
    "bolívar",
    "sánchez carrión",
    "otuzco",
    "pataz",
    "julcán",
    "santiago de chuco",
    "cajatambo",
    "huarochirí",
    "yauyos"
]
z5 =  [
    "Bolognesi", "Huaraz", "Pomabamba", "Recuay", "Antabamba", "Grau", 
    "Caylloma", "Huanca Sancos", "Sucre", "Víctor Fajardo", "Canas", 
    "Espinar", "Chumbivilcas", "Huancavelica", "Lauricocha", "Dos de Mayo", 
    "Junín", "Pasco", "Azángaro", "Lampa", "Melgar", "Moho", "San Román", "Tacna"
]

z6 = [
    "Mariscal Luzuriaga",
    "Cotabambas",
    "a La Unión",
    "Lucanas",
    "Parinacochas",
    "Angaraes",
    "Oyón",
    "Daniel Alcides Carrión",
    "Carabaya",
    "Chucuito",
    "El Collao",
    "Huancané",
    "Puno",
    "Yunguyo",
    "Candarave",
    "Tarata"
]

z7= [
    "Chachapoyas",
    "Utcubamba",
    "Bongará",
    "Luya",
    "Rodríguez de Mendoza",
    "Pallasca",
    "Abancay",
    "Chincheros",
    "Huanta",
    "La Mar",
    "Vilcashuamán",
    "Cajabamba",
    "Cajamarca",
    "Celendín",
    "Chota",
    "Contumazá",
    "Cutervo",
    "Hualgayoc",
    "Jaén",
    "San Marcos",
    "San Ignacio",
    "San Pablo",
    "Santa Cruz",
    "Tayacaja",
    "Ambo",
    "Huacaybamba",
    "Marañón",
    "Yarowilca",
    "Gran Chimú",
    "Manu",
    "Ayabaca",
    "Rioja"
]

z8 = [
    "La Convención",
    "Leoncio Prado",
    "Puerto Inca",
    "Chanchamayo",
    "Satipo",
    "Lambayeque",
    "Tahuamanu",
    "Tambopata",
    "Oxapampa",
    "Huancabamba",
    "Morropón",
    "Sullana",
    "San Antonio de Putina",
    "Sandia",
    "Tumbes",
    "Zarumilla"
]

z9 = [
    "Bagua",
    "Condorcanqui",
    "Maynas",
    "Alto Amazonas",
    "Loreto",
    "Mariscal Ramón Castilla",
    "Requena",
    "Datem del Marañón",
    "Ucayali",
    "Bellavista",
    "Mariscal Cáceres",
    "San Martín",
    "El Dorado",
    "Huallaga",
    "Lamas",
    "Moyobamba",
    "Picota",
    "Tocache",
    "Purús",
    "Padre Abad",
    "Atalaya",
    "Coronel Portillo"
]

const = {
    "techo concreto": ["zona_1", "zona_2"],
    "teja andina": ["zona_3", "zona_4"],
}

def get_tipo_techo(zona):
    
    for tipo_techo, zonas in const.items():
        if zona in zonas:
            return tipo_techo
    return "Tipo de techo desconocido"

def convert_lower_array(arr):
    return [item.strip().lower() for item in arr]

def get_zona_provincia(provincia):
    provincia = provincia.strip().lower()
    
    if provincia in convert_lower_array(z1):
        return "zona_1", get_tipo_techo("zona_1")
    elif provincia in convert_lower_array(z2):
        return "zona_2", get_tipo_techo("zona_2")
    elif provincia in convert_lower_array(z3):
        return "zona_3", get_tipo_techo("zona_3")
    elif provincia in convert_lower_array(z4):
        return "zona_4", get_tipo_techo("zona_4")
    elif provincia in convert_lower_array(z5):
        return "zona_5", get_tipo_techo("zona_5")
    elif provincia in convert_lower_array(z6):
        return "zona_6", get_tipo_techo("zona_6")
    elif provincia in convert_lower_array(z7):
        return "zona_7", get_tipo_techo("zona_7")
    elif provincia in convert_lower_array(z8):
        return "zona_8", get_tipo_techo("zona_8")
    elif provincia in convert_lower_array(z9):
        return "zona_9", get_tipo_techo("zona_9")
    else:
        return "Zona desconocida", "Tipo de techo desconocido"