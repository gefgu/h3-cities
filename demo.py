import streamlit as st

st.set_page_config(page_title="H3-Cities - Moved")
st.title("H3-Cities")

st.info("🚀 **This app has moved to a new location!**")

st.markdown(
    """
    ### App Relocated
    
    The H3-Cities application is now running at a new location with improved performance and reliability.
    
    **New URL:** https://h3-cities.vercel.app/
    
    Please update your bookmarks and use the button below to access the application.
    """
)

st.link_button(
    "🏙️ Go to H3-Cities App", "https://h3-cities.vercel.app/", use_container_width=True
)

st.markdown(
    """
    ---
    
    **What is H3-Cities?**
    
    H3-Cities is a tool that generates hexagonal grids for cities using the H3 geospatial indexing system. 
    You can visualize and download city boundaries as hexagonal tessellations at different resolutions.
    """
)
