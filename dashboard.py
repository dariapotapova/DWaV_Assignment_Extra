import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="IT Jobs Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Мятно-голубая цветовая схема
MINT_GREEN = "#98FB98"
SKY_BLUE = "#87CEEB"
DEEP_MINT = "#3CB371"
DEEP_SKY = "#00BFFF"
PALE_MINT = "#E0F8E0"
PALE_BLUE = "#EBF5FB"
WHITE = "#FFFFFF"
DARK_TEXT = "#2C3E50"

# Кастомный CSS для мятно-голубого дизайна
st.markdown(f"""
    <style>
        /* Основной фон */
        .stApp {{
            background: linear-gradient(135deg, {PALE_BLUE} 0%, {PALE_MINT} 100%);
        }}
        
        /* Сайдбар */
        div[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {PALE_MINT} 0%, {PALE_BLUE} 100%);
            border-right: 2px solid {DEEP_MINT};
        }}
        
        /* Заголовки */
        h1, h2, h3 {{
            color: {DEEP_SKY} !important;
            font-weight: 600 !important;
        }}
        
        /* Метрики */
        div[data-testid="stMetricValue"] {{
            color: {DEEP_MINT} !important;
            font-size: 2rem !important;
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {DEEP_SKY} !important;
        }}
        
        /* Табы */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {PALE_BLUE};
            border-radius: 10px;
            padding: 10px 20px;
            color: {DARK_TEXT};
            border: 1px solid {SKY_BLUE};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {DEEP_MINT} 0%, {DEEP_SKY} 100%);
            color: {WHITE};
            border: none;
        }}
        
        /* Мультиселект */
        div[data-baseweb="select"] {{
            background-color: {WHITE};
            border-radius: 8px;
        }}
        
        /* Кнопки */
        button {{
            background: linear-gradient(135deg, {DEEP_MINT} 0%, {DEEP_SKY} 100%) !important;
            color: {WHITE} !important;
            border: none !important;
            border-radius: 8px !important;
        }}
        
        button:hover {{
            transform: scale(1.02);
            transition: 0.3s;
        }}
        
        /* Капшн */
        .stCaption {{
            color: {DARK_TEXT} !important;
        }}
        
        /* Разделитель */
        hr {{
            border-color: {SKY_BLUE} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("IT Vacancies: Russian vs International Market")
st.markdown("---")

@st.cache_data
def load_data():
    habr = pd.read_csv('data/clean/habr_clean.csv')
    themuse = pd.read_csv('data/clean/themuse_clean.csv')

    habr['region'] = 'Russia'
    themuse['region'] = 'International'

    df = pd.concat([habr, themuse], ignore_index=True)
    df_russia = df[df['region'] == 'Russia']
    df_int = df[df['region'] == 'International']

    return df, df_russia, df_int

df, df_russia, df_int = load_data()

with st.sidebar:
    st.markdown("## Filters")

    all_categories = sorted(df['category'].unique())
    selected_categories = st.multiselect(
        "Job Categories",
        options=all_categories,
        default=all_categories
    )

    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown(f"- Russia: Habr Career (587 vacancies)")
    st.markdown(f"- International: The Muse API (3783 vacancies)")

tab1, tab2 = st.tabs(["Russia Market", "International Market"])

with tab1:
    st.header("Russian IT Job Market")
    st.caption(f"Total vacancies: {len(df_russia)}")

    df_russia_filtered = df_russia[df_russia['category'].isin(selected_categories)] if selected_categories else df_russia

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Categories")
        cat_counts = df_russia_filtered['category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig1 = px.bar(cat_counts, x='Category', y='Count', title="Vacancies by Category", text='Count')
        fig1.update_traces(textposition='outside', marker_color=SKY_BLUE)
        fig1.update_layout(showlegend=False, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Remote vs Office")
        remote_counts = df_russia_filtered['remote'].value_counts().reset_index()
        remote_counts.columns = ['Remote', 'Count']
        remote_counts['Remote'] = remote_counts['Remote'].map({True: 'Remote', False: 'Office'})
        fig2 = px.pie(remote_counts, values='Count', names='Remote', title="Work Format", hole=0.3)
        fig2.update_traces(marker_colors=[DEEP_MINT, SKY_BLUE])
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Seniority Levels")
        level_counts = df_russia_filtered['level'].value_counts().reset_index()
        level_counts.columns = ['Level', 'Count']
        fig3 = px.bar(level_counts, x='Level', y='Count', title="Seniority Distribution", text='Count')
        fig3.update_traces(textposition='outside', marker_color=DEEP_MINT)
        fig3.update_layout(showlegend=False, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Top Companies (All)")
        company_counts = df_russia_filtered['company'].value_counts().head(10).reset_index()
        company_counts.columns = ['Company', 'Count']
        fig4 = px.bar(company_counts, x='Count', y='Company', orientation='h', title="Top 10 Employers", text='Count')
        fig4.update_traces(textposition='outside', marker_color=SKY_BLUE)
        fig4.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Top Cities")
    city_counts = df_russia_filtered['city'].value_counts().head(10).reset_index()
    city_counts.columns = ['City', 'Count']
    fig5 = px.bar(city_counts, x='City', y='Count', title="Vacancies by City", text='Count')
    fig5.update_traces(textposition='outside', marker_color=DEEP_SKY)
    fig5.update_layout(showlegend=False, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig5, use_container_width=True)

with tab2:
    st.header("International IT Job Market")
    st.caption(f"Total vacancies: {len(df_int)}")

    df_int_filtered = df_int[df_int['category'].isin(selected_categories)] if selected_categories else df_int

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Categories")
        cat_counts_int = df_int_filtered['category'].value_counts().reset_index()
        cat_counts_int.columns = ['Category', 'Count']
        fig6 = px.bar(cat_counts_int, x='Category', y='Count', title="Vacancies by Category", text='Count')
        fig6.update_traces(textposition='outside', marker_color=SKY_BLUE)
        fig6.update_layout(showlegend=False, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        st.subheader("Remote vs Office")
        remote_counts_int = df_int_filtered['remote'].value_counts().reset_index()
        remote_counts_int.columns = ['Remote', 'Count']
        remote_counts_int['Remote'] = remote_counts_int['Remote'].map({True: 'Remote', False: 'Office'})
        fig7 = px.pie(remote_counts_int, values='Count', names='Remote', title="Work Format", hole=0.3)
        fig7.update_traces(marker_colors=[DEEP_MINT, SKY_BLUE])
        fig7.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig7, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Seniority Levels")
        level_counts_int = df_int_filtered['level'].value_counts().reset_index()
        level_counts_int.columns = ['Level', 'Count']
        fig8 = px.bar(level_counts_int, x='Level', y='Count', title="Seniority Distribution", text='Count')
        fig8.update_traces(textposition='outside', marker_color=DEEP_MINT)
        fig8.update_layout(showlegend=False, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig8, use_container_width=True)

    with col4:
        st.subheader("Top Companies (All)")
        company_counts_int = df_int_filtered['company'].value_counts().head(10).reset_index()
        company_counts_int.columns = ['Company', 'Count']
        fig9 = px.bar(company_counts_int, x='Count', y='Company', orientation='h', title="Top 10 Employers", text='Count')
        fig9.update_traces(textposition='outside', marker_color=SKY_BLUE)
        fig9.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Top Countries")
    country_counts_int = df_int_filtered['country'].value_counts().head(10).reset_index()
    country_counts_int.columns = ['Country', 'Count']
    fig10 = px.bar(country_counts_int, x='Country', y='Count', title="Vacancies by Country", text='Count')
    fig10.update_traces(textposition='outside', marker_color=DEEP_SKY)
    fig10.update_layout(showlegend=False, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig10, use_container_width=True)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #3CB371; padding: 20px;'>Data sources: Habr Career (Russia) | The Muse API (International)</div>",
    unsafe_allow_html=True
)