
import streamlit as st
import pandas as pd
import numpy as np

########### COLORE BOTTONE ################
m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #00ff00;
    color:#ff0000;
    }
</style>""", unsafe_allow_html=True)

def conv_time_float(value):
    vals = value.split(':')
    t, hours = divmod(float(vals[0]), 24)
    t, minutes = divmod(float(vals[1]), 60)
    minutes = minutes / 60.0
    return hours + minutes



def main():
    st.title("Bifor Data Transformation")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['pausa'] = df['Total Meal Break'].apply(conv_time_float)
        df['notturno'] = df['End Time'].apply(conv_time_float)
        df['notturno'].mask(df['notturno'] > 7, 0, inplace=True)
        df['totale'] = df['Total Time']
        df['data'] = df['Start Date']

        df = df[['Team Member','data','notturno','totale']]
        from itertools import cycle

        ##repeat
        df2 = df.loc[df.index.repeat(3)].reset_index(drop=True)

        num_cycle = cycle([1, 2, 3])
        df2['cat'] = [next(num_cycle) for num in range(len(df2))]

        ## repeat
        df2 = df2.replace({'cat': {1: '_totale', 2: 'di cui notturni',3:'permessi'}})

        df2['notturno'].mask(df2['cat'] == '_totale', 0, inplace=True)
        df2['totale'].mask(df2['cat'] == 'di cui notturni', 0, inplace=True)
        df2['notturno'].mask(df2['cat'] == 'permessi', 0, inplace=True)
        df2['totale'].mask(df2['cat'] == 'permessi', 0, inplace=True)

        df2['ore'] = df2['notturno']+df2['totale']
        df2 = df2[['Team Member','data','cat','ore']]

        multi = df2.set_index(['Team Member', 'cat'])
        multi['data'] = multi['data'].astype(str)
        multi = multi.pivot(columns='data')
        multi = multi.replace(np.nan,0)

        #multi.to_excel('ciao17.xlsx')

        with st.spinner("Processing Data..."):
            st.balloons()
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                st.dataframe(multi)
                multi.to_excel(writer)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()
                st.download_button(
                    label="Download Excel Report",
                    data=buffer,
                    file_name="final_result.xlsx",
                    mime="application/vnd.ms-excel")
                
                # if st.button('Publish G-sheet'):

                #     # 1 ######## append  to google sheet ######################
                #     #id=https://docs.google.com/spreadsheets/d/1GU0fTDaMPlwK7VecwlrBoCDNHvdLaGmGVvKgNmMIhDM/edit#gid=0
                #     #condivedere il google sheet con la mail:"python@iron-pottery-342915.iam.gserviceaccount.com"
                #     df = df.fillna('')
                #     gsheetId = '1GU0fTDaMPlwK7VecwlrBoCDNHvdLaGmGVvKgNmMIhDM'
                #     gc = gs.service_account(filename="new_bigquery.json")
                #     sh = gc.open_by_key(gsheetId)
                #     worksheet = sh.get_worksheet(0)#index sheet inside file
                #     #data_list = df.values.tolist() 
                #     #worksheet.append_rows(data_list)

                #     worksheet.clear() #clear sheet
                #     #replace all values
                #     worksheet.update([df.columns.values.tolist()] + df.values.tolist())
                #     st.write('Published on GoogleSheet!')
                #     st.write("check GoogleSheet at this [link](https://docs.google.com/spreadsheets/d/1GU0fTDaMPlwK7VecwlrBoCDNHvdLaGmGVvKgNmMIhDM/edit#gid=0)")

    ###### transformation #####################################

if __name__ == "__main__":
    main()