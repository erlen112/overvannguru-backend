from flask import Flask, request, jsonify
from flask_cors import CORS
import geopandas as gpd
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

app = Flask(__name__)
CORS(app)

# ✅ Full oversettelse av AR5-koder
AR5_KODE_NAVN = {
    "10": "Fulldyrka jord",
    "11": "Fulldyrka jord – åpen åker",
    "12": "Fulldyrka jord – eng",
    "20": "Overflatedyrka jord",
    "30": "Innmarksbeite",
    "40": "Produktiv skog",
    "41": "Skog med høy bonitet",
    "42": "Skog med middels bonitet",
    "43": "Skog med lav bonitet",
    "44": "Uproduktiv skog",
    "50": "Åpen fastmark i fjellet",
    "51": "Bjørkeskoggrenseområde",
    "52": "Snaufjell",
    "60": "Åpen fastmark – lav produktivitet",
    "70": "Åpen fastmark – høy produktivitet",
    "80": "Bebygd område",
    "81": "Tettbebyggelse",
    "82": "Industri / næringsområde",
    "83": "Samferdselsanlegg og teknisk infrastruktur",
    "90": "Myrområde",
    "91": "Elv / innsjø",
    "92": "Våtmark med åpen vannflate",
    "93": "Våtmark uten åpen vannflate",
    "99": "Uklassifisert areal",
    "U": "Ukjent / udefinert",
    "A": "Åpen fastmark",
    "B": "Bebygd område",
    "F": "Skog",
    "G": "Fulldyrka jord",
    "H": "Overflatedyrka jord",
    "I": "Innmarksbeite",
    "L": "Vann",
    "M": "Myr",
    "T": "Lauvskog",
    "V": "Samferdsel"
}

# 🔁 Areal i m²
def calculate_area_m2(geom):
    return transform(lambda x, y: (x, y), geom).area

# 🗺️ Les AR5
ar5_path = r"C:\Users\erlen\OneDrive\Skrivebord\Andre ting til OG\0000_25833_ar50_gdb.gdb"
ar5_data = gpd.read_file(ar5_path)
print(f"🗂️ Lest inn {len(ar5_data)} AR5-flater")
print("🧭 Datasett-CRS:", ar5_data.crs)
print("🗺️ AR5-dekning:", ar5_data.total_bounds)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    if not data or "polygon" not in data:
        return jsonify({"error": "Ingen polygon mottatt"}), 400

    try:
        # 🌍 Mottar polygon fra frontend i WGS84
        geojson_polygon = shape(data["polygon"])

        # 🔄 Konverter til EPSG:25833
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:25833", always_xy=True).transform
        transformed_polygon = transform(transformer, geojson_polygon)
        print("📐 Transformert polygon:", transformed_polygon)

        # 🔍 Finn overlapp
        result = {}
        for _, row in ar5_data.iterrows():
            if row.geometry.intersects(transformed_polygon):
                overlap = row.geometry.intersection(transformed_polygon)
                area_m2 = calculate_area_m2(overlap)
                if area_m2 > 0:
                    kode = str(row.get("artype", "U"))
                    navn = AR5_KODE_NAVN.get(kode, f"Ukjent arealtype ({kode})")
                    result[navn] = result.get(navn, 0) + round(area_m2, 2)

        return jsonify(result)

    except Exception as e:
        print("❌ Feil:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

