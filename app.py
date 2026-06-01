import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Prediksi Harga Mobil Bekas",
    page_icon="🚗",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv("ford.csv")

    data = df.copy()

    tahun_sekarang = 2026
    data["car_age"] = tahun_sekarang - data["year"]

    data = data[["car_age", "mileage", "tax", "mpg", "engineSize", "price"]]

    data = data.dropna()

    data = data[
        (data["car_age"] >= 0) &
        (data["car_age"] <= 40) &
        (data["mileage"] >= 0) &
        (data["tax"] >= 0) &
        (data["mpg"] > 0) &
        (data["engineSize"] > 0) &
        (data["price"] > 0)
    ]

    data = data.sample(5000, random_state=42).reset_index(drop=True)

    return data


data = load_data()


def turun(x, a, b):
    if x <= a:
        return 1
    elif x >= b:
        return 0
    else:
        return (b - x) / (b - a)


def naik(x, a, b):
    if x <= a:
        return 0
    elif x >= b:
        return 1
    else:
        return (x - a) / (b - a)


def segitiga(x, a, b, c):
    if x <= a or x >= c:
        return 0
    elif x == b:
        return 1
    elif x < b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)


def get_quantile_params(series):
    q1 = series.quantile(0.25)
    q2 = series.quantile(0.50)
    q3 = series.quantile(0.75)
    return q1, q2, q3


params = {}

for col in ["car_age", "mileage", "tax", "mpg", "engineSize", "price"]:
    params[col] = get_quantile_params(data[col])


def fuzzifikasi(row):
    hasil = {}

    q1, q2, q3 = params["car_age"]
    hasil["car_age_muda"] = turun(row["car_age"], q1, q2)
    hasil["car_age_sedang"] = segitiga(row["car_age"], q1, q2, q3)
    hasil["car_age_tua"] = naik(row["car_age"], q2, q3)

    q1, q2, q3 = params["mileage"]
    hasil["mileage_rendah"] = turun(row["mileage"], q1, q2)
    hasil["mileage_sedang"] = segitiga(row["mileage"], q1, q2, q3)
    hasil["mileage_tinggi"] = naik(row["mileage"], q2, q3)

    q1, q2, q3 = params["tax"]
    hasil["tax_rendah"] = turun(row["tax"], q1, q2)
    hasil["tax_sedang"] = segitiga(row["tax"], q1, q2, q3)
    hasil["tax_tinggi"] = naik(row["tax"], q2, q3)

    q1, q2, q3 = params["mpg"]
    hasil["mpg_boros"] = turun(row["mpg"], q1, q2)
    hasil["mpg_sedang"] = segitiga(row["mpg"], q1, q2, q3)
    hasil["mpg_irit"] = naik(row["mpg"], q2, q3)

    q1, q2, q3 = params["engineSize"]
    hasil["engineSize_kecil"] = turun(row["engineSize"], q1, q2)
    hasil["engineSize_sedang"] = segitiga(row["engineSize"], q1, q2, q3)
    hasil["engineSize_besar"] = naik(row["engineSize"], q2, q3)

    return hasil


rules = [
    {
        "No": 1,
        "Kondisi": [("car_age", "muda"), ("mileage", "rendah"), ("engineSize", "besar")],
        "Output": "tinggi",
        "Rule": "Jika usia mobil muda DAN mileage rendah DAN mesin besar maka harga tinggi"
    },
    {
        "No": 2,
        "Kondisi": [("car_age", "muda"), ("mileage", "rendah"), ("mpg", "irit")],
        "Output": "tinggi",
        "Rule": "Jika usia mobil muda DAN mileage rendah DAN mpg irit maka harga tinggi"
    },
    {
        "No": 3,
        "Kondisi": [("car_age", "muda"), ("mileage", "sedang"), ("engineSize", "sedang")],
        "Output": "tinggi",
        "Rule": "Jika usia mobil muda DAN mileage sedang DAN mesin sedang maka harga tinggi"
    },
    {
        "No": 4,
        "Kondisi": [("car_age", "sedang"), ("mileage", "rendah"), ("engineSize", "besar")],
        "Output": "tinggi",
        "Rule": "Jika usia mobil sedang DAN mileage rendah DAN mesin besar maka harga tinggi"
    },
    {
        "No": 5,
        "Kondisi": [("car_age", "muda"), ("tax", "tinggi"), ("engineSize", "besar")],
        "Output": "tinggi",
        "Rule": "Jika usia mobil muda DAN pajak tinggi DAN mesin besar maka harga tinggi"
    },
    {
        "No": 6,
        "Kondisi": [("car_age", "sedang"), ("mileage", "sedang"), ("engineSize", "sedang")],
        "Output": "sedang",
        "Rule": "Jika usia mobil sedang DAN mileage sedang DAN mesin sedang maka harga sedang"
    },
    {
        "No": 7,
        "Kondisi": [("car_age", "sedang"), ("mileage", "rendah"), ("mpg", "sedang")],
        "Output": "sedang",
        "Rule": "Jika usia mobil sedang DAN mileage rendah DAN mpg sedang maka harga sedang"
    },
    {
        "No": 8,
        "Kondisi": [("car_age", "muda"), ("mileage", "tinggi"), ("engineSize", "sedang")],
        "Output": "sedang",
        "Rule": "Jika usia mobil muda DAN mileage tinggi DAN mesin sedang maka harga sedang"
    },
    {
        "No": 9,
        "Kondisi": [("car_age", "tua"), ("mileage", "rendah"), ("engineSize", "besar")],
        "Output": "sedang",
        "Rule": "Jika usia mobil tua DAN mileage rendah DAN mesin besar maka harga sedang"
    },
    {
        "No": 10,
        "Kondisi": [("car_age", "sedang"), ("tax", "sedang"), ("mpg", "sedang")],
        "Output": "sedang",
        "Rule": "Jika usia mobil sedang DAN pajak sedang DAN mpg sedang maka harga sedang"
    },
    {
        "No": 11,
        "Kondisi": [("car_age", "tua"), ("mileage", "tinggi")],
        "Output": "rendah",
        "Rule": "Jika usia mobil tua DAN mileage tinggi maka harga rendah"
    },
    {
        "No": 12,
        "Kondisi": [("car_age", "tua"), ("engineSize", "kecil")],
        "Output": "rendah",
        "Rule": "Jika usia mobil tua DAN mesin kecil maka harga rendah"
    },
    {
        "No": 13,
        "Kondisi": [("mileage", "tinggi"), ("engineSize", "kecil")],
        "Output": "rendah",
        "Rule": "Jika mileage tinggi DAN mesin kecil maka harga rendah"
    },
    {
        "No": 14,
        "Kondisi": [("car_age", "sedang"), ("mileage", "tinggi"), ("mpg", "boros")],
        "Output": "rendah",
        "Rule": "Jika usia mobil sedang DAN mileage tinggi DAN mpg boros maka harga rendah"
    },
    {
        "No": 15,
        "Kondisi": [("car_age", "tua"), ("tax", "tinggi"), ("mpg", "boros")],
        "Output": "rendah",
        "Rule": "Jika usia mobil tua DAN pajak tinggi DAN mpg boros maka harga rendah"
    }
]


def hitung_alpha_rule(fuzzy_values, kondisi):
    nilai_kondisi = []

    for variabel, label in kondisi:
        key = f"{variabel}_{label}"
        nilai_kondisi.append(fuzzy_values[key])

    alpha = min(nilai_kondisi)

    return alpha


def inferensi(row):
    fuzzy_values = fuzzifikasi(row)
    hasil_rules = []

    for rule in rules:
        alpha = hitung_alpha_rule(fuzzy_values, rule["Kondisi"])

        hasil_rules.append({
            "No": rule["No"],
            "Rule": rule["Rule"],
            "Alpha": alpha,
            "Output": rule["Output"]
        })

    return hasil_rules


price_min = data["price"].quantile(0.01)
price_max = data["price"].quantile(0.99)

x_price = np.linspace(price_min, price_max, 500)

q1_price, q2_price, q3_price = params["price"]


def mf_price_rendah(x):
    return turun(x, q1_price, q2_price)


def mf_price_sedang(x):
    return segitiga(x, q1_price, q2_price, q3_price)


def mf_price_tinggi(x):
    return naik(x, q2_price, q3_price)


def prediksi_mamdani(row):
    hasil_rules = inferensi(row)

    agregasi = np.zeros_like(x_price)

    for hasil in hasil_rules:
        alpha = hasil["Alpha"]
        output = hasil["Output"]

        if output == "rendah":
            mf_output = np.array([mf_price_rendah(x) for x in x_price])
        elif output == "sedang":
            mf_output = np.array([mf_price_sedang(x) for x in x_price])
        else:
            mf_output = np.array([mf_price_tinggi(x) for x in x_price])

        implikasi = np.minimum(alpha, mf_output)
        agregasi = np.maximum(agregasi, implikasi)

    if np.sum(agregasi) == 0:
        return q2_price

    hasil_defuzzifikasi = np.sum(x_price * agregasi) / np.sum(agregasi)

    return hasil_defuzzifikasi


z_rendah = q1_price
z_sedang = q2_price
z_tinggi = q3_price


def prediksi_sugeno(row):
    hasil_rules = inferensi(row)

    total_alpha = 0
    total_alpha_z = 0

    for hasil in hasil_rules:
        alpha = hasil["Alpha"]
        output = hasil["Output"]

        if output == "rendah":
            z = z_rendah
        elif output == "sedang":
            z = z_sedang
        else:
            z = z_tinggi

        total_alpha += alpha
        total_alpha_z += alpha * z

    if total_alpha == 0:
        return q2_price

    hasil_akhir = total_alpha_z / total_alpha

    return hasil_akhir


def kategori_harga(nilai):
    if nilai <= q1_price:
        return "Rendah"
    elif nilai <= q3_price:
        return "Sedang"
    else:
        return "Tinggi"


def buat_grafik_mamdani(row):
    hasil_rules = inferensi(row)

    alpha_rendah = 0
    alpha_sedang = 0
    alpha_tinggi = 0

    for hasil in hasil_rules:
        if hasil["Output"] == "rendah":
            alpha_rendah = max(alpha_rendah, hasil["Alpha"])
        elif hasil["Output"] == "sedang":
            alpha_sedang = max(alpha_sedang, hasil["Alpha"])
        elif hasil["Output"] == "tinggi":
            alpha_tinggi = max(alpha_tinggi, hasil["Alpha"])

    y_rendah = np.array([mf_price_rendah(x) for x in x_price])
    y_sedang = np.array([mf_price_sedang(x) for x in x_price])
    y_tinggi = np.array([mf_price_tinggi(x) for x in x_price])

    clip_rendah = np.minimum(alpha_rendah, y_rendah)
    clip_sedang = np.minimum(alpha_sedang, y_sedang)
    clip_tinggi = np.minimum(alpha_tinggi, y_tinggi)

    agregasi = np.maximum.reduce([clip_rendah, clip_sedang, clip_tinggi])

    if np.sum(agregasi) == 0:
        hasil_defuzz = q2_price
    else:
        hasil_defuzz = np.sum(x_price * agregasi) / np.sum(agregasi)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(x_price, y_rendah, label="Harga Rendah")
    ax.plot(x_price, y_sedang, label="Harga Sedang")
    ax.plot(x_price, y_tinggi, label="Harga Tinggi")

    ax.fill_between(x_price, clip_rendah, alpha=0.3)
    ax.fill_between(x_price, clip_sedang, alpha=0.3)
    ax.fill_between(x_price, clip_tinggi, alpha=0.3)

    ax.axvline(hasil_defuzz, linestyle="--", label=f"Defuzzifikasi = {hasil_defuzz:.2f}")

    ax.set_title("Visualisasi Clipping Mamdani")
    ax.set_xlabel("Harga Mobil")
    ax.set_ylabel("Derajat Keanggotaan")
    ax.legend()
    ax.grid(True)

    return fig


st.title("🚗 Prediksi Harga Mobil Bekas")
st.write(
    "Aplikasi ini menggunakan Fuzzy Mamdani dan Fuzzy Sugeno untuk memprediksi harga mobil bekas "
    "berdasarkan spesifikasi dan kondisi kendaraan."
)

st.info(
    "Streamlit hanya digunakan sebagai antarmuka aplikasi. "
    "Proses prediksi tetap dilakukan menggunakan Fuzzy Logic Mamdani dan Sugeno dari scratch."
)

tab1, tab2, tab3 = st.tabs(["Prediksi", "Dataset", "Rule Base"])


with tab1:
    st.subheader("Input Data Mobil")

    col1, col2 = st.columns(2)

    with col1:
        car_age = st.number_input(
            "Usia Mobil",
            min_value=0,
            max_value=40,
            value=5,
            step=1
        )

        mileage = st.number_input(
            "Mileage",
            min_value=0,
            value=30000,
            step=1000
        )

        tax = st.number_input(
            "Tax",
            min_value=0,
            value=150,
            step=10
        )

    with col2:
        mpg = st.number_input(
            "MPG",
            min_value=1.0,
            value=55.0,
            step=0.1
        )

        engineSize = st.number_input(
            "Engine Size",
            min_value=0.1,
            value=1.5,
            step=0.1
        )

    if st.button("Prediksi Harga"):
        input_data = pd.Series({
            "car_age": car_age,
            "mileage": mileage,
            "tax": tax,
            "mpg": mpg,
            "engineSize": engineSize
        })

        hasil_mamdani = prediksi_mamdani(input_data)
        hasil_sugeno = prediksi_sugeno(input_data)

        kategori_mamdani = kategori_harga(hasil_mamdani)
        kategori_sugeno = kategori_harga(hasil_sugeno)

        st.subheader("Hasil Prediksi")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Prediksi Mamdani",
                f"£ {hasil_mamdani:,.2f}",
                kategori_mamdani
            )

        with col2:
            st.metric(
                "Prediksi Sugeno",
                f"£ {hasil_sugeno:,.2f}",
                kategori_sugeno
            )

        selisih = abs(hasil_mamdani - hasil_sugeno)

        st.write(f"Selisih hasil prediksi Mamdani dan Sugeno: **£ {selisih:,.2f}**")

        st.subheader("Hasil Fuzzifikasi")

        fuzzy_values = fuzzifikasi(input_data)

        fuzzifikasi_df = pd.DataFrame({
            "Himpunan Fuzzy": list(fuzzy_values.keys()),
            "Derajat Keanggotaan": list(fuzzy_values.values())
        })

        st.dataframe(fuzzifikasi_df, use_container_width=True)

        st.subheader("Hasil Inferensi Rule")

        inferensi_df = pd.DataFrame(inferensi(input_data))
        st.dataframe(inferensi_df, use_container_width=True)

        st.subheader("Grafik Clipping Mamdani")

        fig = buat_grafik_mamdani(input_data)
        st.pyplot(fig)


with tab2:
    st.subheader("Dataset yang Digunakan")

    st.write("Dataset: **UK Used Car Dataset**, subset **ford.csv**")
    st.write("Jumlah data yang digunakan setelah preprocessing:", data.shape[0])
    st.write("Jumlah kolom:", data.shape[1])

    st.dataframe(data.head(20), use_container_width=True)

    st.subheader("Variabel Input dan Output")

    variabel_df = pd.DataFrame({
        "Nama Variabel": [
            "car_age",
            "mileage",
            "tax",
            "mpg",
            "engineSize",
            "price"
        ],
        "Jenis": [
            "Input",
            "Input",
            "Input",
            "Input",
            "Input",
            "Output"
        ],
        "Keterangan": [
            "Usia mobil berdasarkan tahun produksi",
            "Jarak tempuh mobil",
            "Pajak kendaraan",
            "Efisiensi bahan bakar",
            "Kapasitas mesin",
            "Harga mobil bekas"
        ]
    })

    st.dataframe(variabel_df, use_container_width=True)


with tab3:
    st.subheader("Rule Base")

    rule_df = pd.DataFrame({
        "No": [r["No"] for r in rules],
        "Rule": [r["Rule"] for r in rules],
        "Output": [r["Output"].capitalize() for r in rules]
    })

    st.dataframe(rule_df, use_container_width=True)

    st.subheader("Konstanta Output Sugeno")

    sugeno_output_df = pd.DataFrame({
        "Kategori Output": ["Rendah", "Sedang", "Tinggi"],
        "Nilai Konstanta Sugeno": [z_rendah, z_sedang, z_tinggi]
    })

    st.dataframe(sugeno_output_df, use_container_width=True)