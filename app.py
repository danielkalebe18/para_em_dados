from flask import Flask, render_template_string, request
import folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
import unicodedata
import re

app = Flask(__name__)

# ==========================================
# ARQUIVOS DOS DADOS
# ==========================================

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
            border: none;
            cursor: pointer;
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
            height: calc(100vh - 290px);
            min-height: 450px;
        }

        .mapa-container iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        .pesquisa {
            background: white;
            padding: 18px;
            margin: 15px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
        }

        .campo-pesquisa {
            width: 100%;
            max-width: 500px;
            padding: 12px;
            border: 1px solid #9caec2;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }

        .opcoes {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        .opcoes label {
            cursor: pointer;
            font-size: 14px;
        }

        .mensagem {
            color: #17365d;
            font-size: 14px;
            margin-top: 12px;
        }

        @media (max-width: 600px) {
            .conteudo {
                margin: 15px auto;
                padding: 12px;
            }

            .card h2 {
                font-size: 26px;
            }

            .mapa-container {
                height: 65vh;
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
    return render_template_string(HTML, conteudo=conteudo)


# ==========================================
# FUNÇÃO DE NORMALIZAÇÃO DE NOMES
# ==========================================

def normalizar_nome(nome):
    nome = str(nome).strip().lower()
    nome = unicodedata.normalize("NFKD", nome)

    nome = "".join(
        caractere for caractere in nome
        if not unicodedata.combining(caractere)
    )

    return re.sub(r"\s+", " ", nome)


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
                <p>Pesquise qualquer município ou visualize
                os setores censitários de todo o estado.</p>

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

    setores = setores.to_crs(epsg=4326).copy()

    setores["v0001"] = pd.to_numeric(
        setores["v0001"],
        errors="coerce"
    )

    mapa = folium.Map(
        location=localizacao,
        zoom_start=zoom,
        tiles=None,
        control_scale=True
    )

    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Tiles ©️ Esri",
        name="Imagem de satélite",
        overlay=False,
        control=True,
        max_zoom=19
    ).add_to(mapa)

    valores = setores["v0001"].dropna()

    if not valores.empty:

        minimo = valores.min()
        maximo = valores.max()

        if minimo == maximo:
            maximo = minimo + 1

        escala = cm.LinearColormap(
            colors=["#ffffcc", "#fd8d3c", "#bd0026"],
            vmin=minimo,
            vmax=maximo,
            caption="População por setor censitário"
        )

        def estilo(feature):
            valor = feature["properties"].get("v0001")

            try:
                valor = float(valor)
                cor = escala(valor)
            except (TypeError, ValueError):
                cor = "#cccccc"

            return {
                "fillColor": cor,
                "color": "#333333",
                "weight": 0.5,
                "fillOpacity": 0.65
            }

        campos = [
            campo for campo in ["CD_SETOR", "NM_MUN", "v0001"]
            if campo in setores.columns
        ]

        aliases = {
            "CD_SETOR": "Código do setor:",
            "NM_MUN": "Município:",
            "v0001": "Total de pessoas:"
        }

        folium.GeoJson(
            data=setores.to_json(),
            name="População por setor",
            style_function=estilo,

            highlight_function=lambda feature: {
                "weight": 2,
                "color": "#000000",
                "fillOpacity": 0.85
            },

            tooltip=folium.GeoJsonTooltip(
                fields=campos,
                aliases=[aliases[campo] for campo in campos],
                localize=True
            )

        ).add_to(mapa)

        escala.add_to(mapa)

    return mapa


# ==========================================
# FUNÇÃO PARA ADICIONAR SETORES DIRETAMENTE
# AO MAPA DO PARÁ
# ==========================================

def adicionar_setores(mapa, setores, nome_camada):

    setores = setores.to_crs(epsg=4326).copy()

    setores["v0001"] = pd.to_numeric(
        setores["v0001"],
        errors="coerce"
    )

    grupo = folium.FeatureGroup(
        name=nome_camada,
        show=True
    )

    valores = setores["v0001"].dropna()

    if valores.empty:
        return

    minimo = valores.min()
    maximo = valores.max()

    if minimo == maximo:
        maximo = minimo + 1

    escala = cm.LinearColormap(
        colors=["#ffffcc", "#fd8d3c", "#bd0026"],
        vmin=minimo,
        vmax=maximo,
        caption="População por setor censitário"
    )

    def estilo(feature):

        valor = feature["properties"].get("v0001")

        try:
            valor = float(valor)
            cor = escala(valor)
        except (TypeError, ValueError):
            cor = "#cccccc"

        return {
            "fillColor": cor,
            "color": "#333333",
            "weight": 0.5,
            "fillOpacity": 0.65
        }

    campos = [
        campo for campo in ["CD_SETOR", "NM_MUN", "v0001"]
        if campo in setores.columns
    ]

    aliases = {
        "CD_SETOR": "Código do setor:",
        "NM_MUN": "Município:",
        "v0001": "Total de pessoas:"
    }

    folium.GeoJson(
        data=setores.to_json(),
        name=nome_camada,
        style_function=estilo,

        highlight_function=lambda feature: {
            "weight": 2,
            "color": "#000000",
            "fillOpacity": 0.85
        },

        tooltip=folium.GeoJsonTooltip(
            fields=campos,
            aliases=[aliases[campo] for campo in campos],
            localize=True
        )

    ).add_to(grupo)

    grupo.add_to(mapa)
    escala.add_to(mapa)


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
# MAPA DE TODO O PARÁ COM PESQUISA
# ==========================================

@app.route("/para")
def mapa_para():

    # Carregar os setores do Pará
    setores = gpd.read_file(ARQUIVO_PARA)

    # Transformar as coordenadas para latitude e longitude
    setores = setores.to_crs(epsg=4326)

    setores["v0001"] = pd.to_numeric(
        setores["v0001"],
        errors="coerce"
    )

    # Lista de municípios disponíveis
    municipios = sorted(
        setores["NM_MUN"].dropna().astype(str).unique().tolist()
    )

    # Município pesquisado
    municipio = request.args.get("municipio", "").strip()

    mostrar_municipio = (
        request.args.get("mostrar_municipio") == "1"
    )

    mostrar_para = (
        request.args.get("mostrar_para") == "1"
    )

    # ======================================
    # ENCONTRAR MUNICÍPIO
    # ======================================

    setores_municipio = None
    municipio_encontrado = None

    if municipio:

        municipio_normalizado = normalizar_nome(municipio)

        nomes_normalizados = setores["NM_MUN"].fillna("").map(
            normalizar_nome
        )

        filtro = nomes_normalizados == municipio_normalizado

        if filtro.any():

            setores_municipio = setores.loc[filtro].copy()

            municipio_encontrado = setores_municipio[
                "NM_MUN"
            ].iloc[0]

    # ======================================
    # CRIAR MAPA PRINCIPAL
    # ======================================

    mapa = folium.Map(
        location=[-3.8, -52.5],
        zoom_start=6,
        tiles=None,
        control_scale=True
    )

    # Fundo de satélite
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Tiles ©️ Esri",
        name="Imagem de satélite",
        overlay=False,
        control=True,
        max_zoom=19
    ).add_to(mapa)

    # ======================================
    # MOSTRAR CONTORNO DO MUNICÍPIO
    # ======================================

    if setores_municipio is not None:

        limite_municipio = setores_municipio[
            ["geometry"]
        ].dissolve()

        folium.GeoJson(
            data=limite_municipio.to_json(),
            name="Limite do município",

            style_function=lambda feature: {
                "fillColor": "#00ffff",
                "color": "#00ffff",
                "weight": 3,
                "fillOpacity": 0.08
            },

            tooltip=municipio_encontrado

        ).add_to(mapa)

    # ======================================
    # MOSTRAR SETORES DO MUNICÍPIO
    # ======================================

    if mostrar_municipio and setores_municipio is not None:

        adicionar_setores(
            mapa,
            setores_municipio,
            "Setores censitários do município"
        )

    # ======================================
    # MOSTRAR SETORES DO PARÁ INTEIRO
    # ======================================

    if mostrar_para:

        adicionar_setores(
            mapa,
            setores,
            "Setores censitários do Pará inteiro"
        )

    # ======================================
    # APROXIMAR AUTOMATICAMENTE O MUNICÍPIO
    # ======================================

    if setores_municipio is not None:

        # Garantir que os limites estejam em EPSG:4326
        setores_zoom = setores_municipio.to_crs(epsg=4326)

        minx, miny, maxx, maxy = setores_zoom.total_bounds

        mapa.fit_bounds(
            [
                [miny, minx],
                [maxy, maxx]
            ],
            padding=(10, 10),
            max_zoom=16
        )

    # ======================================
    # VISÃO GERAL DO PARÁ
    # ======================================

    elif mostrar_para or not municipio:

        minx, miny, maxx, maxy = setores.total_bounds

        mapa.fit_bounds(
            [
                [miny, minx],
                [maxy, maxx]
            ],
            padding=(20, 20)
        )

    # Controle das camadas
    folium.LayerControl(collapsed=False).add_to(mapa)

    # ======================================
    # INTERFACE DE PESQUISA
    # ======================================

    conteudo = """
    <div class="pesquisa">

        <h2>Pesquisar município do Pará</h2>

        <form method="GET" action="/para">

            <input
                class="campo-pesquisa"
                type="text"
                name="municipio"
                list="lista-municipios"
                placeholder="Digite o nome da cidade..."
                value="{{ municipio }}"
                autocomplete="off"
            >

            <datalist id="lista-municipios">
                {% for nome in municipios %}
                    <option value="{{ nome }}"></option>
                {% endfor %}
            </datalist>

            <button class="botao" type="submit">
                Pesquisar
            </button>

            <a class="botao secundario" href="/para">
                Limpar
            </a>

            <div class="opcoes">

                <label>
                    <input
                        type="checkbox"
                        name="mostrar_municipio"
                        value="1"
                        {% if mostrar_municipio %}checked{% endif %}
                        onchange="this.form.submit()"
                    >
                    Mostrar setores do município
                </label>

                <label>
                    <input
                        type="checkbox"
                        name="mostrar_para"
                        value="1"
                        {% if mostrar_para %}checked{% endif %}
                        onchange="this.form.submit()"
                    >
                    Mostrar setores do Pará inteiro
                </label>

            </div>

        </form>

        {% if municipio_encontrado %}
            <p class="mensagem">
                Município selecionado:
                <strong>{{ municipio_encontrado }}</strong>
            </p>

        {% elif municipio %}
            <p class="mensagem">
                Município não encontrado. Confira o nome digitado.
            </p>

        {% else %}
            <p class="mensagem">
                Pesquise uma cidade ou escolha uma das camadas
                para visualizar os setores.
            </p>
        {% endif %}

    </div>

    <div class="mapa-container">
        {{ mapa_html|safe }}
    </div>
    """

    conteudo_renderizado = render_template_string(
        conteudo,
        mapa_html=mapa._repr_html_(),
        municipios=municipios,
        municipio=municipio,
        municipio_encontrado=municipio_encontrado,
        mostrar_municipio=mostrar_municipio,
        mostrar_para=mostrar_para
    )

    return mostrar_pagina(conteudo_renderizado)


# ==========================================
# EXECUTAR O SISTEMA
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)