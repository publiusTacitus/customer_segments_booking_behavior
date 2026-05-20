import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from assets.translations import *


@st.cache_data
def load_data(csv_name):
    csv_folder = "assets/query_output_csvs/"
    return pd.read_csv(csv_folder + csv_name)


profiles = load_data("traveller_type_profile.csv")
age_groups = load_data("traveller_type_age_group_breakdown.csv")
classes = load_data("cabin_preference_by_age_and_gender.csv")
lead_times = load_data("traveller_type_lead_time_bin_breakdown.csv")


profiles = profiles.rename(columns={
    "traveller_type_id": "Segment",
    "dominant_loyalty_status": "Dominant Loyalty Status",
    "secondary_loyalty_status": "Secondary Loyalty Status",
    "customer_share_pct": "Customer Share",
    "female_ratio_pct": "Female Ratio",
    "booking_share_pct": "Booking Share",
    "avg_yrly_bkgs_per_cust": "Yearly Bookings per Customer",
    "median_age": "Median Age",
    "avg_bkg_lead_time_days": "Avg Lead Time (Days)",
    "avg_final_to_base_price_ratio": "Final/Base Fare Ratio",
    "premium_cabin_usage_pct": "Premium Cabin Usage",
    "avg_check_in_rate_pct": "Check-In Rate"
})


age_groups["age_group_within_segment"] = (
    (age_groups["customer_share_pct"]
     / age_groups.groupby("traveller_type_id")["customer_share_pct"].transform("sum")
     ) * 100
)

age_groups = age_groups.rename(columns={
    "traveller_type_id": "Segment",
    "age_group": "Age Group",
    "customer_share_pct": "Customer Share",
    "female_ratio_pct": "Female Ratio",
    "male_ratio_pct": "Male Ratio",
    "booking_share_pct": "Booking Share",
    "premium_cabin_usage_pct": "Premium Cabin Usage",
    "avg_check_in_rate_pct": "Check-In Rate",
    "avg_bkg_lead_time_days": "Avg Lead Time (Days)",
    "avg_final_to_base_price_ratio": "Final/Base Fare Ratio",
    "age_group_within_segment": "Age Group within Segment"
})

classes = classes.rename(columns={
    "cabin_class": "Cabin Class",
    "age_group": "Age Group",
    "gender": "Gender",
    "booking_share_pct": "Booking Share",
    "avg_check_in_rate_pct": "Check-In Rate"
})


lead_times["segment_booking_share"] = (
    (lead_times["booking_share_pct"]
     / lead_times.groupby("traveller_type_id")["booking_share_pct"].transform("sum")
     ) * 100
)

lead_times = lead_times.rename(columns={
    "traveller_type_id": "Segment",
    "lead_time_bin": "Lead Time",
    "booking_share_pct": "Booking Share",
    "premium_cabin_usage_pct": "Premium Cabin Usage",
    "avg_bkg_lead_time_days": "Avg Lead Time (Days)",
    "avg_final_to_base_price_ratio": "Final/Base Fare Ratio",
    "share_above_base_price_pct": "Share Above Base Price",
    "share_below_base_price_pct": "Share Below Base Price",
    "segment_booking_share": "Segment Booking Share"
})

lead_plot = lead_times.copy()
lt = lead_plot["Lead Time"]
lead_plot["Lead Time"] = np.select(
    [
        lt == "(1) <= 3 days", lt == "(2) <= 7 days", lt == "(3) <= 14 days",
        lt == "(4) <= 30 days", lt == "(5) <= 60 days", lt == "(6) > 60 days"
    ],
    [
        "1–3 Days", "4–7 Days", "8–14 Days",
        "15–30 Days", "31–60 Days", "60+ Days"
    ], default="Unknown"
)


def localize_columns(df):
    for col in df.columns:
        if col in CL.keys():
            df = df.rename(columns={col: CL[col]})
    return df


def fmt(val, decimals=1, lang_="English"):
    if pd.isna(val):
        return ""
    if lang_ == "Deutsch":
        return f"{val:.{decimals}f}".replace(".", ",")
    return f"{val:.{decimals}f}"


fmt_0 = lambda x: fmt(x, 0, lang)
fmt_1 = lambda x: fmt(x, 1, lang)
fmt_2 = lambda x: fmt(x, 2, lang)
fmt_3 = lambda x: fmt(x, 3, lang)

# -------------------
# Segment Positioning
# -------------------


def create_profile_chart(profiles_, size_view_):

    profiles_plot = profiles_[profiles_[CL["Segment"]] != "ALL_TYPES"].copy()
    profiles_plot[CL["Segment"]] = (profiles_plot[CL["Segment"]].str.replace(r"\(\d+\)\s*", "", regex=True))
    profiles_plot[CL["Segment"]] = profiles_plot[CL["Segment"]].map(S)

    size_col = (CL["Customer Share"] if size_view_ == R["Customer Base Perspective"] else CL["Booking Share"])
    other_share  = (CL["Booking Share"] if size_view_ == R["Customer Base Perspective"] else CL["Customer Share"])

    x_min = profiles_plot[CL["Avg Lead Time (Days)"]].min()
    x_max = profiles_plot[CL["Avg Lead Time (Days)"]].max()
    x_mean = profiles_plot[CL["Avg Lead Time (Days)"]].mean()
    y_mean = profiles_plot[CL["Final/Base Fare Ratio"]].mean()

    y_min = profiles_plot[CL["Final/Base Fare Ratio"]].min()
    y_max = profiles_plot[CL["Final/Base Fare Ratio"]].max()

    segment_colors = {
        S["Leisure"]: "#2A9D8F",
        S["Family"]: "#7A9E48",
        S["Corporate"]: "#F58518",
        S["Road warrior"]: "#E45756"
    }

    fig = px.scatter(
        profiles_plot,
        x=CL["Avg Lead Time (Days)"],
        y=CL["Final/Base Fare Ratio"],
        size=size_col,
        size_max=40,
        text=CL["Segment"],
        color=CL["Segment"],
        color_discrete_map=segment_colors,
        custom_data=[
            profiles_plot[CL["Avg Lead Time (Days)"]].apply(lambda x: fmt_0(x)),
            profiles_plot[CL["Final/Base Fare Ratio"]].apply(lambda x: fmt_2(x)),
            profiles_plot[size_col].apply(lambda x: fmt_1(x)),
            profiles_plot[other_share].apply(lambda x: fmt_1(x)),
            profiles_plot[CL["Female Ratio"]].apply(lambda x: fmt_1(x)),
            profiles_plot[CL["Yearly Bookings per Customer"]].apply(lambda x: fmt_1(x)),
            profiles_plot[CL["Premium Cabin Usage"]].apply(lambda x: fmt_1(x)),
            profiles_plot[CL["Check-In Rate"]].apply(lambda x: fmt_1(x)),
        ]
    )

    fig.update_traces(hovertemplate=
        "<b>%{text}</b><br><br>" +
        f"{CL["Avg Lead Time"]}: " + "%{customdata[0]}" + f" {O["Days"]}<br>" +
        f"{CL["Final/Base Fare Ratio"]}: " + "%{customdata[1]}<br>" +
        f"{size_col}: " + "%{customdata[2]}%<br>" +
        f"{other_share}: " + "%{customdata[3]}%<br><br>" +

        f"{CL["Female Ratio"]}: " + "%{customdata[4]}%<br>" +
        f"{CL["Yearly Bookings per Customer"]}: " + "%{customdata[5]}<br>" +
        f"{CL["Premium Cabin Usage"]}: " + "%{customdata[6]}%<br>" +
        f"{CL["Check-In Rate"]}: " + "%{customdata[7]}%<br>" +
        "<extra></extra>"
    )

    fig.update_layout(showlegend=False)

    fig.update_xaxes(range=[x_min - 5, x_max + 5])

    step = 0.05
    y_min_adj = round(y_min - step, 1)
    y_max_adj = round(y_max + step, 1)
    y_ticks = np.arange(y_min_adj, y_max_adj, step)
    y_text = [f"{t:.2f}".replace(".", ",") if lang == "Deutsch" else f"{t:.2f}" for t in y_ticks]
    fig.update_yaxes(range=[y_min_adj, y_max_adj], tickvals=y_ticks, ticktext=y_text)

    fig.add_vline(x=x_mean, line_dash="dot", line_width=1, line_color="#b0b0b0")
    fig.add_hline(y=y_mean, line_dash="dot", line_width=1, line_color="#b0b0b0")

    fig.update_traces(textposition="top center")
    fig.update_layout(title=dict(text=T["Segment Positioning"], x=0.5, xanchor="center", font=dict(size=24)))

    fig.add_annotation(
        x=0.5,
        y=-0.25,
        xref="paper",
        yref="paper",
        text=CT["Bubble size reflects selected perspective. Reference lines indicate overall averages."],
        showarrow=False
    )

    return fig


# -------------------------------
# Fare Outcomes Across Lead Times
# -------------------------------

def create_lead_time_line_chart(lead_plot_):

    lead_line = lead_plot_.copy()
    lead_line[CL["Segment"]] = lead_line[CL["Segment"]].str.replace(r"\(\d+\)\s*", "", regex=True)
    lead_line[CL["Segment"]] = lead_line[CL["Segment"]].map(S)
    lead_line[CL["Lead Time"]] = lead_line[CL["Lead Time"]].str.replace("Days", O["Days"])

    # minor distortion for better visibility
    y = lead_line[CL["Premium Cabin Usage"]].copy()
    y = np.where(lead_line[CL["Segment"]] == "Family", y + 0.05, y)
    y = np.where(lead_line[CL["Segment"]] == "Leisure", y + 0.2, y)

    segment_colors = {
        S["Leisure"]: "#2A9D8F",
        S["Family"]: "#7A9E48",
        S["Corporate"]: "#F58518",
        S["Road warrior"]: "#E45756"
    }

    fig = px.line(
        lead_line,
        x=CL["Lead Time"],
        y=y,
        color=CL["Segment"],
        color_discrete_map=segment_colors,
        markers=True,
        custom_data=[
            lead_line[CL["Premium Cabin Usage"]].apply(lambda x: fmt_2(x)),
            lead_line[CL["Segment Booking Share"]].apply(lambda x: fmt_2(x)),
            lead_line[CL["Avg Lead Time (Days)"]].apply(lambda x: fmt_0(x))
        ]
    )

    fig.update_traces(
        hovertemplate=
        "<b>%{x}</b><br><br>" +
        f"{CL["Premium Cabin Usage"]}: " + "%{customdata[0]}%<br>" +
        f"{CL["Segment Booking Share"]}: " + "%{customdata[1]}%<br>" +
        f"{CL["Avg Lead Time"]}: " + "%{customdata[2]}" + f" {O['Days']}<br>" +
        "<extra></extra>"
    )

    fig.update_yaxes(title=CL["Premium Cabin Usage"])

    fig.update_layout(
        title=dict(text=T["Premium Cabin Usage Across Lead Times"], x=0.5, xanchor="center", font=dict(size=24))
    )

    return fig


# --------------------------
# Age Composition by Segment
# --------------------------

def create_age_bar_chart(age_groups_, gender_view_):

    age_plot = age_groups_.copy()
    age_plot[CL["Segment"]] = age_plot[CL["Segment"]].str.replace(r"\(\d+\)\s*", "", regex=True)
    age_plot[CL["Segment"]] = age_plot[CL["Segment"]].map(S)

    age_plot["label"] = np.where(
        age_plot[CL["Age Group within Segment"]] >= 10,
            age_plot[CL["Female Ratio"]].apply(lambda x: fmt_1(x)) + f"% {O["Women"]}"
            if gender_view_ == R["Show Gender Shares"] else
            age_plot[CL["Age Group within Segment"]].apply(lambda x: fmt_1(x)) + "%"
        ,""
    )

    age_plot[CL["Age Group"]] = age_plot[CL["Age Group"]].str.replace("Age", O["Age"], regex=True)

    age_colors = {
        f"{O["Age"]} 18–24": "#c6dbef",
        f"{O["Age"]} 25–34": "#9ecae1",
        f"{O["Age"]} 35–44": "#6baed6",
        f"{O["Age"]} 45–60": "#3182bd",
        f"{O["Age"]} 61+": "#08519c"
    }

    fig = px.bar(
        age_plot,
        x=CL["Segment"],
        y=CL["Age Group within Segment"],
        color=CL["Age Group"],
        color_discrete_map=age_colors,
        text="label",
        barmode="stack",
        custom_data=[
            age_plot[CL["Age Group"]],
            age_plot[CL["Age Group within Segment"]].apply(lambda x: fmt_1(x)),
            age_plot[CL["Female Ratio"]].apply(lambda x: fmt_1(x)),
            age_plot[CL["Avg Lead Time (Days)"]].apply(lambda x: fmt_0(x)),
            age_plot[CL["Check-In Rate"]].apply(lambda x: fmt_1(x))
        ]
    )

    fig.update_traces(
        hovertemplate=
        "<b>%{customdata[0]}</b><br><br>" +
        f"{CL["Age Group within Segment"]}: " + "%{customdata[1]}%<br>" +
        f"{CL["Female Ratio"]}: " + "%{customdata[2]}%<br>" +
        f"{CL["Avg Lead Time"]}: " + "%{customdata[3]}" + f" {O["Days"]}<br>" +
        f"{CL["Check-In Rate"]}: " + "%{customdata[4]}%<br>" +
        "<extra></extra>"
    )

    fig.update_yaxes(ticksuffix="%")
    fig.update_layout(legend_traceorder="reversed")
    fig.update_traces(textposition="inside", textfont_size=10, insidetextanchor="middle")

    title=[
        T["Age Composition by Segment (+ Gender Labels)"] if gender_view_ == R["Show Gender Shares"]
        else T["Age Composition by Segment"],
    ][0]

    fig.update_layout(title=dict(text=title, x=0.5, xanchor="center", font=dict(size=24)))

    fig.add_annotation(
        x=0.5,
        y=-0.25,
        xref="paper",
        yref="paper",
        text=CT["Bars show age composition within each segment. Reference lines indicate overall averages."],
        showarrow=False
    )

    return fig


# ----------------------------------
# Booking Timing Patterns by Segment
# ----------------------------------

def create_lead_time_bar_chart(lead_plot_):

    lead_bar = lead_plot_.copy()
    lead_bar[CL["Segment"]] = lead_bar[CL["Segment"]].str.replace(r"\(\d+\)\s*", "", regex=True)
    lead_bar[CL["Segment"]] = lead_bar[CL["Segment"]].map(S)
    lead_bar[CL["Lead Time"]] = lead_bar[CL["Lead Time"]].str.replace("Days", O["Days"])

    lead_bar["label"] = np.where(
        lead_bar[CL["Segment Booking Share"]] >= 10,
        lead_bar[CL["Segment Booking Share"]].apply(lambda x: fmt_1(x)) + "%",
        ""
    )

    lead_colors = {
        f"1–3 {O["Days"]}": "#3f007d",
        f"4–7 {O["Days"]}": "#54278f",
        f"8–14 {O["Days"]}": "#6a51a3",
        f"15–30 {O["Days"]}": "#807dba",
        f"31–60 {O["Days"]}": "#9e9ac8",
        f"60+ {O["Days"]}": "#bcbddc"
    }

    fig = px.bar(
        lead_bar,
        x=CL["Segment"],
        y=CL["Segment Booking Share"],
        color=CL["Lead Time"],
        color_discrete_map=lead_colors,
        text="label",
        barmode="stack",
        custom_data = [
            CL["Lead Time"],
            lead_bar[CL["Segment Booking Share"]].apply(lambda x: fmt_1(x)),
            lead_bar[CL["Avg Lead Time (Days)"]].apply(lambda x: fmt_0(x)),
            lead_bar[CL["Premium Cabin Usage"]].apply(lambda x: fmt_1(x))
        ]
    )

    fig.update_traces(
        hovertemplate=
        f"<b>{O["Lead Time"]}: " + "%{customdata[0]}</b><br><br>" +
        f"{CL["Segment Booking Share"]}: " + "%{customdata[1]}%<br>" +
        f"{CL["Avg Lead Time"]}: " + "%{customdata[2]}" + f" {O["Days"]}<br>" +
        f"{CL["Premium Cabin Usage"]}: " + "%{customdata[3]}%<br>" +
        f"<extra></extra>"
    )

    fig.update_yaxes(ticksuffix="%")
    fig.update_layout(legend_traceorder="reversed")
    fig.update_traces(textposition="inside", textfont_size=10, insidetextanchor="middle")

    fig.update_layout(
        title=dict(text=T["Booking Timing Patterns by Segment"], x=0.5, xanchor="center", font=dict(size=24))
    )

    return fig


# -----------------------------
# Cabin Preference by Age Group
# -----------------------------

def create_cabin_heatmap(classes_):

    cabin_plot = classes_[(classes_[CL["Gender"]] == "OVERALL")].copy()
    cabin_plot[CL["Age Group"]] = cabin_plot[CL["Age Group"]].str.replace("Age", O["Age"], regex=True)

    heat = cabin_plot.pivot(index=CL["Age Group"], columns=CL["Cabin Class"], values=CL["Booking Share"]).iloc[::-1]
    checkin = cabin_plot.pivot(index=CL["Age Group"], columns=CL["Cabin Class"], values=CL["Check-In Rate"]).iloc[::-1]

    heat.columns = (heat.columns.str.replace(r"\(\d+\)\s*", "", regex=True))
    heat_text = heat.applymap(lambda x: fmt_1(x))
    checkin_text = checkin.applymap(fmt_1)

    heat_norm = (heat - heat.min()) / (heat.max() - heat.min())

    blue_scale = [
        "#c6dbef",
        "#9ecae1",
        "#6baed6",
        "#3182bd",
        "#08519c"
    ]

    fig = px.imshow(
        heat_norm,
        aspect="auto",
        color_continuous_scale=blue_scale
    )

    fig.update_traces(text=heat_text.values, texttemplate="%{text}%")

    fig.update_traces(
        customdata=checkin_text.values,
        hovertemplate=
        "<b>%{y}</b><br><br>" +
        f"{CL['Booking Share']}: " + "%{text}%<br>" +
        f"{CL['Check-In Rate']}: " + "%{customdata}%<br>" +
        "<extra></extra>"
    )

    fig.update_layout(coloraxis_showscale=False)

    fig.update_layout(
        title=dict(text=T["Age Group Differences in Cabin Usage"], x=0.5, xanchor="center", font=dict(size=24))
    )

    return fig


# -------------------------------
# Fare Outcomes Across Lead Times
# -------------------------------

def create_lead_time_heatmap(lead_times_):

    lead_plot_ = lead_times_.copy()

    heat = lead_plot_.pivot(index=CL["Lead Time"], columns=CL["Segment"], values=CL["Final/Base Fare Ratio"])
    heat.columns = (heat.columns.str.replace(r"\(\d+\)\s*", "", regex=True))

    heat.index = [
        f"1–3 {O["Days"]}",
        f"4–7 {O["Days"]}",
        f"8–14 {O["Days"]}",
        f"15–30 {O["Days"]}",
        f"31–60 {O["Days"]}",
        f"60+ {O["Days"]}"
    ]

    heat = heat.reindex(heat.index[::-1], axis=0)
    heat.columns = heat.columns.map(S)

    premium = (
        lead_plot_.pivot(index=CL["Lead Time"], columns=CL["Segment"], values=CL["Premium Cabin Usage"]).iloc[::-1]
    )
    premium.columns = premium.columns.map(S)

    below_base = (
        lead_plot_.pivot(index=CL["Lead Time"], columns=CL["Segment"], values=CL["Share Below Base Price"]).iloc[::-1]
    )
    below_base.columns = below_base.columns.map(S)

    heat_text = heat.applymap(lambda x: fmt_2(x))
    premium_text = premium.applymap(lambda x: fmt_1(x))
    below_base_text = below_base.applymap(lambda x: fmt_1(x))

    custom_data = np.stack([premium_text.values, below_base_text.values], axis=-1)

    purple_scale = [
        "#bcbddc",
        "#9e9ac8",
        "#756bb1",
        "#54278f"
    ]

    fig = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale=purple_scale
    )

    fig.update_yaxes(title=CL["Lead Time"])
    fig.update_traces(text=heat_text.values, texttemplate="%{text}")

    fig.update_traces(
        customdata=custom_data,
        hovertemplate=
        f"<b>{O["Lead Time"]}: " + "%{y}</b><br><br>" +
        f"{CL['Final/Base Fare Ratio']}: " + "%{text}<br>" +
        f"{CL['Premium Cabin Usage']}: " + "%{customdata[0]}%<br>" +
        f"{CL['Share Below Base Price']}: " + "%{customdata[1]}%<br>" +
        "<extra></extra>"
    )

    fig.update_layout(coloraxis_showscale=False)

    fig.update_layout(
        title=dict(text=T["Fare Outcomes Across Lead Times"], x=0.5, xanchor="center", font=dict(size=24))
    )

    return fig


# ---------
# DASHBOARD
# ---------

params = st.query_params

if "lang" not in st.session_state:
    st.session_state.lang = (
        "Deutsch" if params.get("lang") == "de"
        else "English"
    )

with st.container(border=False, gap=None, horizontal_alignment="center"):
    st.segmented_control(
        "", ("English", "Deutsch"), key="lang", label_visibility="collapsed"
    )

    lang = st.session_state.lang
    st.query_params["lang"] = "de" if lang == "Deutsch" else "en"

    CL, S, CT, T, R, O = columns[lang], segments[lang], captions[lang], titles[lang], radios[lang], other[lang]

    st.set_page_config(page_title=T["Customer Segments and Booking Behavior"], layout="wide")
    st.title(T["Customer Segments and Booking Behavior"], text_alignment="center")

profiles, age_groups, classes = localize_columns(profiles), localize_columns(age_groups), localize_columns(classes)
lead_times, lead_plot = localize_columns(lead_times), localize_columns(lead_plot)


col1, col2, col3 = st.columns([1, 0.02, 1])

with col1:

    # -------------------
    # Segment Positioning
    # -------------------

    col1.space("xxsmall")
    with st.container(height=500, border=False, gap=None):
        chart_slot_1 = st.empty()

    sub1a, sub1b = st.columns([1.5, 4])
    with sub1b:
        size_view = st.radio(
            "",
            [R["Customer Base Perspective"], R["Booking Activity Perspective"]],
            horizontal=True, label_visibility="collapsed"
        )
    col1.space("medium")

    fig_tt = create_profile_chart(profiles, size_view)
    chart_slot_1.plotly_chart(fig_tt, use_container_width=True, height=475)

    # -------------------------------------
    # Premium Cabin Usage Across Lead Times
    # -------------------------------------

    #col1.space("xxsmall")
    fig_premium = create_lead_time_line_chart(lead_plot)
    st.plotly_chart(fig_premium, use_container_width=True, height=500)

    # ----------------------------------
    # Booking Timing Patterns by Segment
    # ----------------------------------

    fig_lt_bars = create_lead_time_bar_chart(lead_plot)
    st.plotly_chart(fig_lt_bars, use_container_width=True, height=500)


with col3:

    # --------------------------
    # Age Composition by Segment
    # --------------------------

    col3.space("xxsmall")
    with st.container(height=500, border=False, gap=None):
        chart_slot_2 = st.empty()

    sub2a, sub2b = st.columns([1.5, 4])
    with sub2b:
        gender_view = st.radio(
            "",
            [R["Hide Gender Shares"], R["Show Gender Shares"]],
            horizontal=True, label_visibility="collapsed"
        )
    col3.space("medium")

    fig_age = create_age_bar_chart(age_groups, gender_view)
    chart_slot_2.plotly_chart(fig_age, use_container_width=True, height=475)

    # -----------------------------
    # Cabin Preference by Age Group
    # -----------------------------

    #col3.space("xxsmall")
    fig_cabin = create_cabin_heatmap(classes)
    st.plotly_chart(fig_cabin, use_container_width=True, height=500)

    # -------------------------------
    # Fare Outcomes Across Lead Times
    # -------------------------------

    fig_lt_heat = create_lead_time_heatmap(lead_times)
    st.plotly_chart(fig_lt_heat, use_container_width=True, height=500)


st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "<a href='https://github.com/publiusTacitus/customer_segments_booking_behavior'>GitHub</a> • "
    "<a href='https://www.linkedin.com/in/jan-heinrich-sch%C3%BCttler-64b872396/'>LinkedIn</a>"
    "</div>",
    unsafe_allow_html=True
)