import streamlit as st
import pandas as pd
import plotly.express as px    
import plotly.graph_objects as go
import requests
from itertools import cycle

st.set_page_config(layout="wide",page_title="Leaseback Calculator")
st.title("Leaseback Calculator")
st.subheader("A sale-leaseback can help business owners free up capital to grow their business and reduce their debt.")
st.header("Property Details")




with st.form("user_inputs"):
    col1, col2, col3 = st.beta_columns(3)
    with col1:
        st.subheader("Estimated property value ($)")
        prop_value = st.number_input("Not sure how much your property is worth? Contact us and get an estimate within 24 hours.", min_value=0, value=2500000)
        st.subheader("Business industry")
        industry = st.selectbox("", options=['Medical','Veterinary','Restaurant','Industrial','Other'])
    with col2:
        st.subheader("Yearly appreciation (%)")
        annual_apprec = st.number_input("How much do you expect your property to increase in value year over year (not adjusted for inflation)?", min_value=0.0, value=4.5,format='%f')/100
        st.subheader("Return on $ Invested in your Business (%)")
        annual_return = st.number_input("What % return do you expect on capital invested in growing your business?", min_value=1.0, value=20.0,format='%f')/100
    with col3:
        st.subheader("Owned or mortgaged?")
        owned = st.selectbox("", options=['Owned','Mortgaged'])

    mortgage_section = st.beta_expander(label='Mortgage details', expanded=False)

    with mortgage_section:
        col1, col2, col3, col4 = st.beta_columns(4)
        with col1:
            st.subheader("Loan amount ($)")
            loan = st.number_input("Original mortgage loan amount", min_value=0,value=1875000)
        with col2:
            st.subheader("Interest rate (%)")
            loan_interest = st.number_input("", min_value=0.0, value=3.5,format='%f')/100
        with col3:
            st.subheader("Loan origination year")
            origin_year = st.number_input("", min_value=1900, value=2020)
        with col4:
            st.subheader("Amortization (years)")
            loan_term = st.number_input("", min_value=5, value=25)
    
    calculate = st.form_submit_button("Do math")

if calculate:
    # Generate request dictionary
    if owned == 'Owned':
        owned_clean = 'True' 
    if owned == 'Mortgaged':
        owned_clean = 'False' 
    rdict = {
        'prop_value':prop_value,
        'owned':owned_clean,
        'annual_apprec':annual_apprec,
        'annual_return':annual_return,
        # 'industry':industry,
        'loan':loan,
        'loan_interest':loan_interest,
        'loan_term':loan_term,
        'origin_year':origin_year,

    }
    # Send request
    base_url = "https://jsonplaceholder.typicode.com/posts/"
    response = requests.get('https://damirakyan.pythonanywhere.com/calculate',params=rdict)
    url = response.url 
    print(url)
    response_j = response.json()
    chart_df  = pd.read_json(response_j['graph_array'])

    plist = []
    for p in response_j['total_profit']:
        prof = round(p)
        prof = str(prof)
        prof = '$' + prof
        print(prof)
        plist.append(prof)
        print(plist)        
    
    p_val = "# <center> <span style='color:green; margin-bottom:0;padding-bottom:0;'> " + plist[0] + " | " + plist[1] + " | " + plist[2] + "</span></center>"
    print(p_val)
    v1 = str(response_j['equity_unlocked'])
    v1_val = "# <center> <span style='color:green'>  $" + v1 +  "</span></center>"

    v2 = str(response_j['monthly_rent'])
    v2_val = "# <center> <span style='color:gray'>  $" + v2 +  "</span></center>"

    v3 = response_j['net_aan']*100
    v3 = round(v3,1)
    v3 = str(v3)
    v3_val = "# <center> <span style='color:green'>" + v3 +  "%</span></center>"


    roe_fig = px.line(chart_df, x='year', y=["lb_roe","keep_roe"],title="Return on Equity",
    labels={"value": "return on equity",})
    names = cycle(['Leaseback', 'Keep property'])
    roe_fig.for_each_trace(lambda t:  t.update(name = next(names)))
    roe_fig.layout.yaxis.tickformat = ',.0%'
    cprof_fig = px.line(chart_df, x='year', y=["delta_profit_cum"],title="Total profit",labels={"value": "total profit",})
    cprof_fig.update_layout(showlegend=False)

    # st.plotly_chart(kpi_fig)
    st.title("Results")
    st.markdown(p_val,unsafe_allow_html=True)
    st.markdown("### <center> Total profit at 5/10/15 years </center>",unsafe_allow_html=True)
    st.markdown(" ")   

    colh1,colh2,colh3 = st.beta_columns(3)
    with colh1:
        st.markdown(v1_val,unsafe_allow_html=True)
        st.markdown("### <center> Equity Unlocked </center>",unsafe_allow_html=True)

    with colh2:
        st.markdown(v2_val,unsafe_allow_html=True)
        st.markdown("### <center> Monthly rent </center>",unsafe_allow_html=True)
    with colh3:
        st.markdown(v3_val,unsafe_allow_html=True)
        st.markdown("### <center> Net Average Annual Returns </center>",unsafe_allow_html=True)
    st.markdown(" ")   

    colo1, colo2 = st.beta_columns(2)
    with colo1:
        st.plotly_chart(roe_fig)
    with colo2:
        st.plotly_chart(cprof_fig)

    st.header("Under the hood")
    st.subheader("Request")
    st.write(url)
    st.subheader("Response")
    st.write(response_j)

