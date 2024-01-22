import geopandas as gpd
import plotly.express as px
import streamlit as st



# Set page configuration to expand the container
st.set_page_config(layout="wide", page_title="의약품_매출액추정맵")
disease_list = ["불면증"]

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                #GithubIcon {visibility: hidden;}
                
               
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True) 



def load_and_process_data(geojson_path):
    # Read GeoJSON file as GeoDataFrame
    gdf = gpd.read_file(geojson_path)
    
    # Rename the column from "convalescent period" to "name of medical institution"
    gdf.rename(columns={"요양기": "요양기관명"}, inplace=True)
    
    return gdf

def main():
    # Specify GeoJSON file paths
    geojson_seoul_path = "https://raw.githubusercontent.com/zunghun/marketsharemap/main/data/data_seoul_wgs84.geojson"
    geojson_hospital_path = "https://raw.githubusercontent.com/zunghun/marketsharemap/main/data/hospital_wgs84.geojson"

    # Load and preprocess data using GeoDataFrames
    gdf_seoul = load_and_process_data(geojson_seoul_path)
    gdf_hospital = load_and_process_data(geojson_hospital_path)

    # Set Streamlit app title
    st.title("환자수 예측을 통한 해당 의약품 매출액 추정")
    
    
    
    # Convert geometries to WGS 84 CRS
    gdf_seoul = gdf_seoul.to_crs("EPSG:4326")
    gdf_hospital = gdf_hospital.to_crs("EPSG:4326")
    
    # GeoJSON 파일에서 좌표 범위 가져오기
    min_lon, min_lat, max_lon, max_lat = gdf_seoul.geometry.total_bounds
    
    st.sidebar.title("질병 예측 발생률을 활용한 매출액 추정맵")
    st.sidebar.subheader("(Market Share and Revenue Estimation Maps with Disease Prediction Micromaps)")
    st.sidebar.subheader("ⓒ 2023-24 Eden AllLiVE HEALTHCARE R&D. All rights reserved.")
    st.sidebar.markdown("---")
    choice = st.sidebar.selectbox("⦿ 질병 선택", disease_list) 
    # # Create a sidebar for options
    # st.sidebar.header("Options")

    # Create a selection box for choosing the Coroplace Map value
    mapping_options = {
        "서울불면": "서울대학교병원",
        "아산불면": "서울아산병원",
        "삼성불면예": "삼성서울병원"
    }

    # Replace the original values with the corrected names
    gdf_seoul.rename(columns=mapping_options, inplace=True)
    
        
    # Allow the user to select the Coroplace Map value using the corrected names
    selected_value = st.sidebar.selectbox("⦿ 병원선택", list(mapping_options.values()))

    # Create an input box for drug price
    drug_price = st.sidebar.number_input("⦿ 약품단가 ₩", value=0)
    st.sidebar.markdown("---")
    
    # Calculate the total by multiplying drug price and selected value
    total = drug_price * gdf_seoul[selected_value]

    # Display the total
    # st.sidebar.write(f"■ 추정 매출액 ₩ {total.sum():,.0f}")
    st.sidebar.write("⦿ 추정 매출액")
    st.sidebar.write(f"₩ {total.sum():,.0f}")
    
    st.sidebar.markdown("---")
    # Add opacity control to sidebar
    opacity = st.sidebar.slider("⌘ 지도 투명도", min_value=0.0, max_value=1.0, value=1.0)
    
    selected_map_style = st.sidebar.radio("⌘ 배경지도 선택", ["carto-positron", "open-street-map"], index=0)
    st.sidebar.markdown("---")
    
    # Extract data for the selected hospital
    selected_hospital_data = gdf_hospital[gdf_hospital['요양기관명'] == selected_value]

    # Calculate center coordinates after converting to WGS 84 CRS
    center = {"lat": (min_lat + max_lat) / 2, "lon": (min_lon + max_lon) / 2}

    # Create Coroplace Map using Plotly Express Choropleth Mapbox
    fig = px.choropleth_mapbox(
        gdf_seoul,
        geojson=gdf_seoul.geometry,
        locations=gdf_seoul.index,
        color=selected_value,  # Use the selected value for color
        hover_name=gdf_seoul.index,
        color_continuous_scale= [[0, 'white'], [0.5, 'yellow'], [1.0, 'rgb(255, 0, 0)']],  # Set color scale to Viridis
        mapbox_style=selected_map_style,  # Set Mapbox style
        center=center,  # Set center coordinates
        zoom=9,  # Set initial zoom level
        opacity=opacity
    )

     
    # Add hospital points to the map
    hospital_points = px.scatter_mapbox(
            selected_hospital_data,
            lat=selected_hospital_data['geometry'].y,
            lon=selected_hospital_data['geometry'].x,
            text=selected_hospital_data['요양기관명'],
            color_discrete_sequence=["darkgreen"],  # Assign a single color to all hospitals
            size=[3] * len(selected_hospital_data),  # Use a list with a constant value for size
            opacity=opacity
    )
    
    # Customize text font for hospital labels
    hospital_points.update_traces(textfont=dict(color="black", size=12))
    
    # Add hospital points to the choropleth map
    fig.add_trace(hospital_points.data[0])
    
    # fig.update_layout(title_text=f"■ {choice}", height=600)
    
    # Update Mapbox layout to adjust map size
    fig.update_layout(
        title_text=f">> {choice} :   ₩ {total.sum():,.0f}",
        title_font=dict(size=25),
        mapbox=dict(
            center=center,
            zoom=10,  # 초기 줌 레벨 조절
        ),
        width=1200,  # 캔버스 너비 조절
        height=800,  # 캔버스 높이 조절
        
    )

    # Display map generated from Streamlit
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
