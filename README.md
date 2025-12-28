# 🏥 DataViz Chile - Establecimientos de Salud

Aplicación interactiva para visualizar y analizar datos de establecimientos de salud en Chile.
Consume datos en tiempo real desde el portal de datos abiertos del gobierno ([datos.gob.cl](https://datos.gob.cl)) mediante la API CKAN.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Descripción

Esta aplicación permite explorar el registro oficial de establecimientos de salud en Chile, incluyendo:
- Hospitales, consultorios, clínicas y centros de atención
- Distribución por región, comuna y tipo de establecimiento
- Análisis de dependencia administrativa (público/privado)
- Filtros interactivos y descarga de datos

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar o descargar el repositorio**
   ```bash
   cd /ruta/donde/está/el/proyecto
   cd dataviz_chile
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Ejecución

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

## ⚙️ Configuración

### Variables principales (en `app.py`)

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `BASE_URL` | `https://datos.gob.cl` | URL base del portal CKAN |
| `DEFAULT_PACKAGE_ID` | `3bf4cf7c-f638-4735-9a01-f65faae4beca` | ID del dataset |
| `DEFAULT_RESOURCE_ID` | `2c44d782-3365-44e3-aefb-2c8b8363a1bc` | ID del recurso CSV |

### Cambiar dataset

1. Visita [datos.gob.cl](https://datos.gob.cl) y busca otro dataset
2. Obtén el `package_id` y `resource_id` de la URL
3. Modifica las constantes en `app.py`, o
4. Usa la opción "Resource ID personalizado" en el sidebar de la app

## 📊 Endpoints CKAN utilizados

| Endpoint | Uso |
|----------|-----|
| `/api/3/action/package_show` | Obtener metadatos y recursos del dataset |
| `/api/3/action/package_search` | Buscar datasets disponibles |
| Descarga directa del recurso | Obtener el CSV con los datos |

**¿Por qué no usamos `datastore_search`?**  
El recurso seleccionado no está indexado en el DataStore de CKAN, por lo que descargamos el CSV completo y lo procesamos con pandas.

## 🏗️ Estructura del proyecto

```
dataviz_chile/
├── app.py                 # Aplicación Streamlit principal
├── src/
│   ├── __init__.py
│   ├── api_client.py      # Cliente API CKAN (requests)
│   ├── processing.py      # Limpieza y transformaciones (pandas)
│   ├── viz.py             # Gráficos (matplotlib)
│   └── utils.py           # Funciones auxiliares
├── data/                  # (vacío, para samples locales si es necesario)
├── requirements.txt       # Dependencias Python
├── .gitignore
└── README.md
```

## 🎯 Funcionalidades

### Sidebar
- **Selector de recurso**: Cambiar entre recursos CSV disponibles
- **Resource ID personalizado**: Ingresar manualmente si el recurso por defecto falla
- **Filtros**: Región, Tipo de establecimiento, Dependencia administrativa
- **Botón Actualizar**: Limpiar cache y recargar datos

### Vista principal
1. **KPIs**: Total establecimientos, regiones, comunas, % públicos
2. **Gráfico de barras**: Establecimientos por región
3. **Gráfico circular**: Distribución por tipo de establecimiento
4. **Gráfico de dependencia**: Establecimientos por dependencia administrativa
5. **Top 15 comunas**: Comunas con más establecimientos
6. **Tabla de datos**: Con selector de columnas y descarga CSV
7. **Conclusiones**: Insights generados automáticamente

## 🔧 Decisiones de diseño

1. **Descarga completa vs DataStore**: Se optó por descargar el CSV completo porque el recurso no está indexado en el DataStore. Esto permite mayor flexibilidad en el procesamiento.

2. **Cache con TTL**: Se usa `st.cache_data` con TTL de 1 hora para evitar llamadas repetidas a la API y mejorar la experiencia del usuario.

3. **Reintentos**: El cliente API implementa reintentos automáticos (3 intentos con delay de 2 segundos) para manejar fallos transitorios de red.

4. **Filtros en sidebar**: Mantiene la interfaz limpia y permite realizar múltiples filtros simultáneos.

5. **Matplotlib puro**: Se usa matplotlib sin seaborn siguiendo los requisitos del proyecto, con una paleta de colores personalizada.

## ⚠️ Limitaciones

- El `resource_id` puede cambiar si el dataset se actualiza en el portal
- Requiere conexión a internet para cargar los datos
- No se implementa autenticación (la API es pública)
- El dataset puede tener inconsistencias en los datos originales

## 🌐 Despliegue en Streamlit Community Cloud

1. Teniendo tu código en un repositorio privado de GitHub.
2. Inicia sesión en [share.streamlit.io](https://share.streamlit.io).
3. Haz clic en "New app" y selecciona "Use existing repo".
4. Elige tu repositorio del listado (asegúrate de dar permisos a Streamlit para ver tus repos privados si te lo pide).
   - **Repository:** `josemayolCL/databiz`
   - **Branch:** `Subir-a-Github`
   - **Main file path:** `app.py`
5. Haz clic en **"Deploy!"**.
6. Streamlit Cloud instalará automáticamente las dependencias desde `requirements.txt`.

La URL será algo como: `https://databiz.streamlit.app`

## 📝 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## 🙏 Créditos

- **Datos**: [Portal de Datos Abiertos del Gobierno de Chile](https://datos.gob.cl)
- **Dataset**: Establecimientos de Salud - Ministerio de Salud de Chile
