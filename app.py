from flask import Flask, render_template_string
import folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm

app = Flask(__name__)

# Arquivos dos dados
ARQUIVO_MAPA = "data/parauapebas_setores.gpkg"
ARQUIVO_POPULACAO = "data/parauapebas_populacao.csv"
ARQUIVO_PARA = "data_para/para_setores_populacao.gpkg"


# ==========================================
# MODELO DAS PAGINAS
# ==========================================

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Pará em Dados</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            color: #222;
        }

        header {
            background: #17365d;
            color: white;
            padding: 22px;
            text-align: center;
        }

        header h1 {
            margin: 0 0 8px;
        }

        header p {
            margin: 0;
        }

        nav {
            background: #244b77;
            padding: 10px;
            text-align: center;
        }

        nav a {
            color: white;
            text-decoration: none;
            margin: 0 12px;
            font-size: 14px;
        }

        nav a:hover {
            text-decoration: underline;
        }

        .conteudo {
            max-width: 1000px;
            margin: 35px auto;
            padding: 20px;
        }

        .indicadores {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 25px 0;
        }

        .card {
            background: white;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 25px;
            text-align: center;
            flex: 1;
            min-width: 220px;
        }

        .card h2 {
            color: #17365d;
            font-size: 32px;
            margin: 10px 0;
        }

        .botoes {
            text-align: center;
            margin-top: 35px;
        }

        .botao {
            display: inline-block;
            background: #17365d;
            color: white;
            text-decoration: none;
            padding: 13px 22px;
            border-radius: 5px;
            margin: 7px;
        }

        .botao:hover {
            background: #28558a;
        }

        .secundario {
            background: #e2e8f0;
            color: #17365d;
            border: 1px solid #9caec2;
        }

        .secundario:hover {
            background: #cbd5e1;
        }

        .caixa {
            background: white;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 25px;
            margin: 15px 0;
        }

        footer {
            text-align: center;
            padding: 20px;
            border-top: 1px solid #cbd5e1;
            margin-top: 40px;
            color: #555;
        }

        .mapa-container {
            width: 100%;
            height: calc(100vh - 160px);
        }

        .mapa-container iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        @media (max-width: 600px) {
            .conteudo {
                margin: 15px auto;
                padding: 12px;
            }

            .card h2 {
                font-size: 26px;
            }
        }
    </style>
</head>

<body>

    <header>
        <h1>Pará em Dados</h1>
        <p>Distribuição da população por setores censitários</p>
    </header>

    <nav>
        <a href="/">Início</a>
        <a href="/mapa">Mapas</a>
    </nav>

    {{ conteudo|safe }}

    <footer>
        Fonte: IBGE - Censo Demográfico 2022
    </footer>

</body>
</html>
"""


def mostrar_pagina(conteudo):
    return render_template_string(
        HTML,
        conteudo=conteudo
    )


# ==========================================
# TELA INICIAL
# ==========================================

@app.route("/")
def inicio():

    conteudo = """
    <div class="conteudo">

        <h2 style="text-align:center;">
            Indicadores do Pará
        </h2>

        <div class="indicadores">

            <div class="card">
                <h2>8.120.131</h2>
                <p>Habitantes</p>
            </div>

            <div class="card">
                <h2>16.714</h2>
                <p>Setores censitários</p>
            </div>

        </div>

        <div class="botoes">

            <a class="botao" href="/mapa">
                Abrir mapa
            </a>

            <a class="botao secundario" href="/sobre">
                Sobre o trabalho
            </a>

        </div>

    </div>
    """

    return mostrar_pagina(conteudo)


# ==========================================
# SOBRE O TRABALHO
# ==========================================

@app.route("/sobre")
def sobre():

    conteudo = """
    <div class="conteudo">

        <div class="caixa">

            <h2>Sobre o trabalho</h2>

            <p>
                Este projeto tem como objetivo apresentar
                a distribuição da população por setores
                censitários no estado do Pará, utilizando
                dados do Censo Demográfico 2022 do IBGE.
            </p>

            <p>
                O sistema permite visualizar os setores
                censitários em mapas interativos e consultar
                informações de população.
            </p>

            <a class="botao" href="/">
                Voltar ao início
            </a>

        </div>

    </div>
    """

    return mostrar_pagina(conteudo)


# ==========================================
# ESCOLHA DOS MAPAS
# ==========================================

@app.route("/mapa")
def escolher_mapa():

    conteudo = """
    <div class="conteudo">

        <h2 style="text-align:center;">
            Mapas interativos
        </h2>

        <div class="indicadores">

            <div class="card">
                <h3>Parauapebas</h3>
                <p>Visualização dos setores censitários
                do município.</p>

                <a class="botao" href="/parauapebas">
                    Abrir mapa
                </a>
            </div>

            <div class="card">
                <h3>Pará inteiro</h3>
                <p>Visualização dos setores censitários
                de todo o estado.</p>

                <a class="botao" href="/para">
                    Abrir mapa
                </a>
            </div>

        </div>

    </div>
    """

    return mostrar_pagina(conteudo)


# ==========================================
# FUNÇÃO PARA CRIAR OS MAPAS
# ==========================================

def criar_mapa(setores, titulo, localizacao, zoom):

    setores = setores.to_crs(epsg=4326)

    setores["v0001"] = pd.to_numeric(
        setores["v0001"],
        errors="coerce"
    )

    mapa = folium.Map(
        location=localizacao,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True
    )

    escala = cm.LinearColormap(
        colors=["#ffffcc", "#fd8d3c", "#bd0026"],
        vmin=setores["v0001"].min(),
        vmax=setores["v0001"].max(),
        caption="População por setor censitário"
    )

    folium.GeoJson(
        data=setores.to_json(),
        name="População por setor",

        style_function=lambda feature: {
            "fillColor": escala(
                feature["properties"]["v0001"]
            ),
            "color": "#333333",
            "weight": 0.5,
            "fillOpacity": 0.65
        },

        highlight_function=lambda feature: {
            "weight": 2,
            "color": "#000000",
            "fillOpacity": 0.85
        },

        tooltip=folium.GeoJsonTooltip(
            fields=["CD_SETOR", "NM_MUN", "v0001"],
            aliases=[
                "Código do setor:",
                "Município:",
                "Total de pessoas:"
            ],
            localize=True
        )

    ).add_to(mapa)

    escala.add_to(mapa)

    minx, miny, maxx, maxy = setores.total_bounds

    mapa.fit_bounds([
        [miny, minx],
        [maxy, maxx]
    ])

    folium.LayerControl().add_to(mapa)

    return mapa


# ==========================================
# MAPA DE PARAUAPEBAS
# ==========================================

@app.route("/parauapebas")
def parauapebas():

    setores = gpd.read_file(ARQUIVO_MAPA)

    populacao = pd.read_csv(
        ARQUIVO_POPULACAO,
        dtype={"CD_SETOR": str}
    )

    setores = setores.merge(
        populacao[["CD_SETOR", "v0001"]],
        on="CD_SETOR",
        how="left"
    )

    setores["v0001"] = pd.to_numeric(
        setores["v0001"],
        errors="coerce"
    )

    mapa = criar_mapa(
        setores,
        "Parauapebas",
        [-6.0675, -49.9037],
        11
    )

    folium.Marker(
        [-6.0675, -49.9037],
        popup="Parauapebas - Pará",
        tooltip="Parauapebas - PA",
        icon=folium.Icon(color="red")
    ).add_to(mapa)

    conteudo = """
    <div class="mapa-container">
        {{ mapa_html|safe }}
    </div>
    """

    return render_template_string(
        HTML,
        conteudo=render_template_string(
            conteudo,
            mapa_html=mapa._repr_html_()
        )
    )


# ==========================================
# MAPA DE TODO O PARÁ
# ==========================================

@app.route("/para")
def mapa_para():

    setores = gpd.read_file(ARQUIVO_PARA)

    mapa = criar_mapa(
        setores,
        "Pará",
        [-3.8, -52.5],
        6
    )

    conteudo = """
    <div class="mapa-container">
        {{ mapa_html|safe }}
    </div>
    """

    return render_template_string(
        HTML,
        conteudo=render_template_string(
            conteudo,
            mapa_html=mapa._repr_html_()
        )
    )


# ==========================================
# EXECUTAR O SISTEMA
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)