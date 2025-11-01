import streamlit as st
import pandas as pd

st.title("Hello Suffian")
upload_file=st.file_uploader("upload Excel File",type=["xlsx"])

if upload_file:
    try:
        annual_data=pd.read_excel(upload_file)
        required_columns = [
            "Year", "Installed Capacity (MW)", "Generation (GWh)", 
            "Imports (GWh)", "Consumption (GWh)"
        ]

        if all(col in annual_data.columns for col in required_columns):
            st.subheader("Annual Electricity Generation (GWh)")
            # st.bar_chart(annual_data.set_index("Year")["Generation (GWh)"])
            st.bar_chart(annual_data.set_index("Year")["Generation (GWh)"])
            
            st.subheader("Electricity Data Table")
            st.dataframe(annual_data)
        else:
            st.error    


        
    except Exception as e:
        st.error("Error while Processing file")

else:
    st.error("File is Empty")
            
    

