import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj

# 🚨 Sti til AR5-data (GeoDatabase fra Kartverket)
ar5_path = r"C:\Users\erlen\OneDrive\Skrivebord\Andre ting til OG\0000_25833_ar50_gdb.gdb"

# 📍 Testpolygon (øst i Hamar)
polygon_coords = [[
    [11.1003, 60.7889],
    [11.1020, 60.7889],
    [11.1020, 60.7902],
    [11.1003, 60.7902],
    [11.1003, 60.7889]
]]
polygon = Polygon(polygon_coords[0])

# 🔄 Transformer polygon fra WGS84 til UTM-sone 33
project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:25833", always_xy=True).transform
polygon = transform(project, polygon)

print("📐 Transformert polygon:", polygon)

# 📏 Beregn areal
def calculate_area_m2(geom):
    return transform(lambda x, y: (x, y), geom).area

# 🔤 AR5-koder med oversettelse
AR5_KODE_NAVN = {
    "G": "Fulldyrka jord", "H": "Overflatedyrka jord", "I": "Innmarksbeite",
    "F": "Skog", "T": "Skog med lauv", "M": "Myr", "A": "Åpen fastmark",
    "B": "Bebygd område", "V": "Samferdselsareal", "L": "Vann", "U": "Udefinert",
    "30": "Skog – høy bonitet", "31": "Skog – middels bonitet", "32": "Skog – lav bonitet",
    "33": "Skog – uproduktiv", "40": "Myr", "41": "Kantvegetasjon", "42": "Strandeng",
    "43": "Rasmark / blokkmark", "44": "Berg i dagen", "50": "Innmarksbeite",
    "60": "Åpen fastmark – lav produktivitet", "70": "Åpen fastmark – høy produktivitet",
    "80": "Bebygd område", "81": "Bebygd område", "82": "Industri / næring",
    "83": "Samferdsel", "90": "Våtmark", "91": "Elv / innsjø", "92": "Snø / is", "99": "Uklassifisert"
}

# 📥 Les AR5-data
print("🔄 Leser AR5-data...")
ar5_data = gpd.read_file(ar5_path)
print(f"✅ Lest inn {len(ar5_data)} polygoner")
print("🧭 CRS (projeksjon):", ar5_data.crs)
print("🗺️ AR5-dekning (bounding box):", ar5_data.total_bounds)

# 🔎 Analyse
resultat = {}
for _, row in ar5_data.iterrows():
    if row.geometry.intersects(polygon):
        overlap = row.geometry.intersection(polygon)
        areal = calculate_area_m2(overlap)
        if areal > 0:
            kode = str(row.get('artype', 'U'))
            navn = AR5_KODE_NAVN.get(kode, f"Ukjent arealtype ({kode})")
            print(f"🔎 Treff: kode={kode}, navn={navn}, areal={round(areal, 2)} m²")
            resultat[navn] = resultat.get(navn, 0) + round(areal, 2)

# 📋 Resultat
if resultat:
    print("\n📋 Samlet resultat:")
    for navn, areal in resultat.items():
        print(f"  - {navn}: {areal} m²")
else:
    print("\n⚠️ Fant ingen arealtyper innenfor polygonet.")




