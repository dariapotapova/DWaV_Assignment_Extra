import streamlit as st
import csv
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

st.set_page_config(
    page_title="IT Jobs Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Мятно-голубая цветовая схема
MINT = "#98FB98"
DEEP_MINT = "#3CB371"
SKY_BLUE = "#87CEEB"
DEEP_SKY = "#00BFFF"
PALE_MINT = "#E0F8E0"
PALE_BLUE = "#EBF5FB"
OCEAN = "#20B2AA"
DARK_TEXT = "#2C3E50"
LIGHT_TEXT = "#FFFFFF"

st.markdown(f"""
    <style>
        /* Убираем скролл с сайдбара */
        section[data-testid="stSidebar"] > div {{
            overflow-y: hidden !important;
        }}
        
        section[data-testid="stSidebar"] .stSidebarContent {{
            overflow-y: hidden !important;
        }}
        
        /* Основной фон градиент */
        .stApp {{
            background: linear-gradient(135deg, {PALE_BLUE} 0%, {PALE_MINT} 100%);
        }}
        
        /* Тёмная тема */
        @media (prefers-color-scheme: dark) {{
            .stApp {{
                background: linear-gradient(135deg, #0D2B3E 0%, #1A3A2A 100%);
            }}
            h1, h2, h3, .stMarkdown, p, .stCaption {{
                color: {LIGHT_TEXT} !important;
            }}
        }}
        
        /* Сайдбар */
        div[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {PALE_MINT} 0%, {PALE_BLUE} 100%);
        }}
        
        @media (prefers-color-scheme: dark) {{
            div[data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #1A3A2A 0%, #0D2B3E 100%);
                border-right: 2px solid {DEEP_MINT};
            }}
            div[data-testid="stSidebar"] .stMarkdown,
            div[data-testid="stSidebar"] p,
            div[data-testid="stSidebar"] label {{
                color: {LIGHT_TEXT} !important;
            }}
        }}
        
        /* Заголовки */
        h1, h2, h3 {{
            color: {OCEAN} !important;
            font-weight: 600 !important;
        }}
        
        /* Метрики */
        div[data-testid="stMetricValue"] {{
            color: {DEEP_SKY} !important;
            font-size: 2rem !important;
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {DEEP_MINT} !important;
        }}
        
        /* Табы */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: linear-gradient(135deg, {PALE_BLUE} 0%, {PALE_MINT} 100%);
            border-radius: 10px;
            padding: 10px 20px;
            color: {OCEAN};
            border: 1px solid {SKY_BLUE};
        }}
        
        @media (prefers-color-scheme: dark) {{
            .stTabs [data-baseweb="tab"] {{
                background: linear-gradient(135deg, #0D2B3E 0%, #1A3A2A 100%);
                color: {SKY_BLUE};
                border: 1px solid {DEEP_MINT};
            }}
            .stTabs [aria-selected="true"] {{
                background: linear-gradient(135deg, {DEEP_MINT} 0%, {DEEP_SKY} 100%) !important;
                color: white !important;
            }}
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {DEEP_MINT} 0%, {DEEP_SKY} 100%) !important;
            color: white !important;
            border: none;
        }}
        
        /* Кнопки */
        button {{
            background: linear-gradient(135deg, {DEEP_MINT} 0%, {DEEP_SKY} 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
        }}
        
        button:hover {{
            transform: scale(1.02);
            transition: 0.3s;
            opacity: 0.9;
        }}
        
        hr {{
            border-color: {SKY_BLUE} !important;
        }}
        
        .stSelectbox label, .stMultiSelect label {{
            color: {OCEAN} !important;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .stSelectbox label, .stMultiSelect label {{
                color: {SKY_BLUE} !important;
            }}
        }}
        
        .stCaption {{
            color: {OCEAN} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("IT Vacancies: Russian vs International Market")
st.markdown("---")

def load_csv(filepath):
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        return []
    return data

def load_data():
    habr = load_csv('data/clean/habr_clean.csv')
    themuse = load_csv('data/clean/themuse_clean.csv')

    for row in habr:
        row['region'] = 'Russia'
        row['remote'] = row.get('remote', 'False').lower() == 'true'

    for row in themuse:
        row['region'] = 'International'
        row['remote'] = row.get('remote', 'False').lower() == 'true'

    return habr, themuse

habr_data, themuse_data = load_data()

with st.sidebar:
    st.markdown("## Filters")

    all_categories = sorted(set([row.get('category', 'Other IT') for row in habr_data + themuse_data]))
    selected_categories = st.multiselect(
        "Job Categories",
        options=all_categories,
        default=all_categories
    )

    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown(f"Russia: Habr Career ({len(habr_data)} vacancies)")
    st.markdown(f"International: The Muse API ({len(themuse_data)} vacancies)")

tab1, tab2 = st.tabs(["Russia Market", "International Market"])

with tab1:
    st.header("Russian IT Job Market")
    st.caption(f"Total vacancies: {len(habr_data)}")

    filtered = [row for row in habr_data if row.get('category') in selected_categories]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Categories")
        cat_counts = Counter([row.get('category', 'Other IT') for row in filtered])
        cat_df = [{'Category': k, 'Count': v} for k, v in cat_counts.most_common()]
        if cat_df:
            fig1 = px.bar(cat_df, x='Category', y='Count', title="Vacancies by Category", text='Count')
            fig1.update_traces(textposition='outside', marker_color=SKY_BLUE,
                               marker_line_color=DEEP_SKY, marker_line_width=1)
            fig1.update_layout(showlegend=False, height=400,
                               plot_bgcolor='rgba(0,0,0,0)',
                               paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Remote vs Office")
        remote_counts = Counter(['Remote' if row.get('remote') else 'Office' for row in filtered])
        remote_df = [{'Remote': k, 'Count': v} for k, v in remote_counts.items()]
        fig2 = px.pie(remote_df, values='Count', names='Remote', title="Work Format", hole=0.3)
        fig2.update_traces(marker_colors=[DEEP_MINT, SKY_BLUE])
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Seniority Levels")
        level_counts = Counter([row.get('level', 'Not specified') for row in filtered])
        level_df = [{'Level': k, 'Count': v} for k, v in level_counts.most_common()]
        fig3 = px.bar(level_df, x='Level', y='Count', title="Seniority Distribution", text='Count')
        fig3.update_traces(textposition='outside', marker_color=DEEP_MINT,
                           marker_line_color=OCEAN, marker_line_width=1)
        fig3.update_layout(showlegend=False, height=400,
                           plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Top Companies")
        company_counts = Counter([row.get('company', 'Unknown') for row in filtered])
        company_df = [{'Company': k, 'Count': v} for k, v in company_counts.most_common(10)]
        fig4 = px.bar(company_df, x='Count', y='Company', orientation='h',
                      title="Top 10 Employers", text='Count')
        fig4.update_traces(textposition='outside', marker_color=OCEAN,
                           marker_line_color=DEEP_SKY, marker_line_width=1)
        fig4.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Top Cities")
    city_counts = Counter([row.get('city', 'Not specified') for row in filtered
                           if row.get('city') not in [None, '', 'Не указан']])
    city_df = [{'City': k, 'Count': v} for k, v in city_counts.most_common(10)]
    fig5 = px.bar(city_df, x='City', y='Count', title="Vacancies by City", text='Count')
    fig5.update_traces(textposition='outside', marker_color=DEEP_SKY,
                       marker_line_color=DEEP_MINT, marker_line_width=1)
    fig5.update_layout(showlegend=False, height=400,
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig5, use_container_width=True)

with tab2:
    st.header("International IT Job Market")
    st.caption(f"Total vacancies: {len(themuse_data)}")

    filtered_int = [row for row in themuse_data if row.get('category') in selected_categories]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Categories")
        cat_counts_int = Counter([row.get('category', 'Other IT') for row in filtered_int])
        cat_df_int = [{'Category': k, 'Count': v} for k, v in cat_counts_int.most_common()]
        fig6 = px.bar(cat_df_int, x='Category', y='Count', title="Vacancies by Category", text='Count')
        fig6.update_traces(textposition='outside', marker_color=SKY_BLUE,
                           marker_line_color=DEEP_SKY, marker_line_width=1)
        fig6.update_layout(showlegend=False, height=400,
                           plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        st.subheader("Remote vs Office")
        remote_counts_int = Counter(['Remote' if row.get('remote') else 'Office' for row in filtered_int])
        remote_df_int = [{'Remote': k, 'Count': v} for k, v in remote_counts_int.items()]
        fig7 = px.pie(remote_df_int, values='Count', names='Remote', title="Work Format", hole=0.3)
        fig7.update_traces(marker_colors=[DEEP_MINT, SKY_BLUE])
        fig7.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig7, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Seniority Levels")
        level_counts_int = Counter([row.get('level', 'Not specified') for row in filtered_int])
        level_df_int = [{'Level': k, 'Count': v} for k, v in level_counts_int.most_common()]
        fig8 = px.bar(level_df_int, x='Level', y='Count', title="Seniority Distribution", text='Count')
        fig8.update_traces(textposition='outside', marker_color=DEEP_MINT,
                           marker_line_color=OCEAN, marker_line_width=1)
        fig8.update_layout(showlegend=False, height=400,
                           plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig8, use_container_width=True)

    with col4:
        st.subheader("Top Companies")
        company_counts_int = Counter([row.get('company', 'Unknown') for row in filtered_int])
        company_df_int = [{'Company': k, 'Count': v} for k, v in company_counts_int.most_common(10)]
        fig9 = px.bar(company_df_int, x='Count', y='Company', orientation='h',
                      title="Top 10 Employers", text='Count')
        fig9.update_traces(textposition='outside', marker_color=OCEAN,
                           marker_line_color=DEEP_SKY, marker_line_width=1)
        fig9.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Top Countries")
    country_counts_int = Counter([row.get('country', 'Not specified') for row in filtered_int
                                  if row.get('country') not in [None, '', 'Не указана']])
    country_df_int = [{'Country': k, 'Count': v} for k, v in country_counts_int.most_common(10)]
    fig10 = px.bar(country_df_int, x='Country', y='Count', title="Vacancies by Country", text='Count')
    fig10.update_traces(textposition='outside', marker_color=DEEP_SKY,
                        marker_line_color=DEEP_MINT, marker_line_width=1)
    fig10.update_layout(showlegend=False, height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig10, use_container_width=True)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #20B2AA; padding: 20px;'>Data sources: Habr Career (Russia) | The Muse API (International)</div>",
    unsafe_allow_html=True
)