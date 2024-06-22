import contextily as cx
import matplotlib.pyplot as plt
import geopandas as gdf
import streamlit as st
from h3cities import get_city_hexagons_geo_df


def clean_string(s: str):
    return s.replace(" ", "_").replace(",", "_")


def plot_city_hexagons(city_name: str, city: gdf.GeoDataFrame):
    f, ax = plt.subplots(1, 1, dpi=300)

    city.plot(ax=ax, alpha=0.4, edgecolor="black")
    cx.add_basemap(ax, crs=city.crs, source=cx.providers.CartoDB.Positron)
    plt.title(city_name)
    ax.set_axis_off()
    return f


st.set_page_config(page_title="H3-Cities")
st.title("H3-Cities First Demo!")

city_name = st.text_input("City Name:", "Paris, France")
resolution = st.slider("Resolution:", 5, 12, 8)


city = get_city_hexagons_geo_df(city_name, resolution)
fig = plot_city_hexagons(city_name, city)

save_path = f"{clean_string(city_name)}_resolution_{resolution}.geojson"

city.to_file(save_path, driver="GeoJSON")
if fig:
    st.pyplot(fig)
else:
    st.write("Sorry... We couldn't find the data you wanted :(")
with open(save_path, "rb") as f:
    st.download_button("Export GeoJSON (.geojson)", f, file_name=save_path)
