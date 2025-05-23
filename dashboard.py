# this is the document for the dashboard


# ----- IMPORTS N THINGS ----- #
import streamlit as st
import json
from datetime import datetime, timezone
from collections import Counter
import matplotlib.pyplot as plt

from cookies import scrape_cookies
from cookie_classifier import score_cookies

import requests



# ----- PAGE NAVIGATION ----- #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select the radio button corresponding to the type of data you'd like to see.", # title
                        ["Visual Summary",   # pages options
                         "Per-Domain Data",
                         "Website Checker",
                         "Data Explanation"])

with open("cookies_output.json", "r")      as data1: cookie_data   = json.load(data1)
with open("2025-05-11_test_all.json", "r") as data2: cookie_scores = json.load(data2)




# ----- OVERALL VARIABLES ----- #
domains = [entry['domain'] for entry in cookie_data]

# Constants from classifier
CREATION_TIME = datetime(2025, 4, 22, 23, 0, 0, tzinfo=timezone.utc).timestamp()
ONE_WEEK = 60 * 60 * 24 * 7
ONE_MONTH = 60 * 60 * 24 * 30

# categorizing the cookies score splits
GOOD = 8
MODERATE = 14

# color orders
expiration_order = ["Short-lived", "Medium-lived", "Long-lived"]
http_only_order = ["True", "False"]
secure_order = ["True", "False"]
samesite_order = ["Strict", "Lax", "None", "Unknown"]

# colors
darkgreen = "#1A4734" # colors from https://ar.pinterest.com/pin/473089135876824076/
green = "#418B24"
yellow = "#F9DD9C"
red = "#E90C00"
darkred = "#870903"
gray = "gray"

expiration_colors = {
    "Short-lived": green,
    "Medium-lived": yellow,
    "Long-lived": red
}

http_only_colors = {
    "True": green,
    "False": red
}

secure_colors = {
    "True": green,
    "False": red
}

samesite_colors = {
    "Strict": darkgreen,
    "Lax": green,
    "None": red,
    "Unknown": gray
}

pie_colors = [green, yellow, red]  # Good, Moderate, Bad

# map domain to cookie scores
score_map = {}
for entry in cookie_scores:
    if isinstance(entry, list) and len(entry) == 2 and isinstance(entry[1], list):
        domain, scores = entry
        score_map[domain] = scores






# ----- FUNCTIONS ----- #
def get_metrics(data):
    expiration_cats = Counter()
    https_cats = Counter()
    secure_cats = Counter()
    samesite_cats = Counter()

    for domain_entry in data:
        for cookie in domain_entry.get("cookies", []):
            if "error" in cookie:
                continue

            expires = cookie.get("expires", -1)
            time_diff = expires - CREATION_TIME
            if time_diff < ONE_WEEK:
                expiration_cats["Short-lived"] += 1
            elif time_diff < ONE_MONTH:
                expiration_cats["Medium-lived"] += 1
            else:
                expiration_cats["Long-lived"] += 1

            https_cats[str(cookie.get("httpOnly", False))] += 1
            secure_cats[str(cookie.get("secure", False))] += 1
            samesite_cats[cookie.get("sameSite", "Unknown")] += 1

    return expiration_cats, https_cats, secure_cats, samesite_cats

def plot_stacked_bar(counter, title, color_map, ordered_labels):
    values = [counter.get(label, 0) for label in ordered_labels]
    colors = [color_map.get(label, "gray") for label in ordered_labels]

    fig, ax = plt.subplots(figsize=(8, 1.2))
    left = 0
    for label, value, color in zip(ordered_labels, values, colors):
        ax.barh([0], [value], left=left, color=color, label=f"{label} ({value})")
        left += value

    ax.set_xlim(0, left)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title(title, fontsize=12)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        fontsize=8,
        frameon=False
    )
    fig.tight_layout()
    st.pyplot(fig)

def categorize_scores(scores):
    categories = {"Good": 0, "Moderate": 0, "Bad": 0}
    for score in scores:
        if score <= GOOD:
            categories["Good"] += 1
        elif score <= MODERATE:
            categories["Moderate"] += 1
        else:
            categories["Bad"] += 1
    return categories

def expiration_category(cookie):
    expires = cookie.get("expires", -1)
    time_diff = expires - CREATION_TIME
    if time_diff < ONE_WEEK:
        return "Short-lived"
    elif time_diff < ONE_MONTH:
        return "Medium-lived"
    else:
        return "Long-lived"

def cookie_matches_filter(cookie, filters):
    return (
        expiration_category(cookie) in filters["expiration"] and
        str(cookie.get("httpOnly", False)) in filters["httpOnly"] and
        str(cookie.get("secure", False)) in filters["secure"] and
        cookie.get("sameSite", "Unknown") in filters["sameSite"]
    )




# ----- ACTUAL BUILD OF THE DASHBOARD ----- #
st.title("Cookie Analysis Dashboard")

if page == "Visual Summary":
    st.subheader("Visual Summary of Cookie Attributes")

    # Default metrics (unfiltered)
    exp, http, sec, same = get_metrics(cookie_data)
    data_to_use = cookie_data

    # Filter section
    with st.expander("Filter Cookies"):
        exp_filters = st.multiselect("Expiration Duration", expiration_order, default=expiration_order)
        http_filters = st.multiselect("HttpOnly Flag", http_only_order, default=http_only_order)
        sec_filters = st.multiselect("Secure Flag", secure_order, default=secure_order)
        same_filters = st.multiselect("SameSite Attribute", samesite_order, default=samesite_order)
        apply = st.button("Apply Filters")

    if apply:
        filters = {
            "expiration": exp_filters,
            "httpOnly": http_filters,
            "secure": sec_filters,
            "sameSite": same_filters
        }

        # Filter the cookie data
        filtered_data = []
        for domain_entry in cookie_data:
            filtered_cookies = [
                c for c in domain_entry.get("cookies", [])
                if "error" not in c and cookie_matches_filter(c, filters)
            ]
            if filtered_cookies:
                filtered_data.append({
                    "domain": domain_entry["domain"],
                    "cookies": filtered_cookies
                })

        # Use filtered data for graphs and table
        data_to_use = filtered_data
        exp, http, sec, same = get_metrics(data_to_use)

    # Render bar charts
    plot_stacked_bar(exp, "Expiration Duration", expiration_colors, expiration_order)
    plot_stacked_bar(http, "HttpOnly Flag", http_only_colors, http_only_order)
    plot_stacked_bar(sec, "Secure Flag", secure_colors, secure_order)
    plot_stacked_bar(same, "SameSite Attribute", samesite_colors, samesite_order)

    st.divider()
    st.subheader("Selected Cookies")

    if apply:
        for domain_entry in data_to_use:
            domain = domain_entry["domain"]
            cookies = domain_entry["cookies"]
            all_cookies = next((d["cookies"] for d in cookie_data if d["domain"] == domain), [])
            if cookies:
                st.markdown(f"### {domain} ({len(cookies)}/{len(all_cookies)})")
                for cookie in cookies:
                    name = cookie.get("name", "(Unnamed Cookie)")
                    exp_days = round((cookie.get("expires", 0) - CREATION_TIME) / (60 * 60 * 24))
                    st.markdown(f"""
                    **{name}**  
                    **Expiration Duration:** {exp_days} days  
                    **HttpOnly Flag:** {cookie.get("httpOnly", False)}  
                    **Secure Flag:** {cookie.get("secure", False)}  
                    **SameSite Attribute:** {cookie.get("sameSite", "Unknown")}  
                    """)

elif page == "Per-Domain Data":
    st.subheader("Per-Domain Cookie Analysis")

    available_domains = sorted([entry['domain'] for entry in cookie_data])
    selected = st.selectbox("Select a domain", available_domains)

    col1, col2 = st.columns([1, 2])

    with col1:
        domain_scores = dict(score_map).get(selected, [])
        score_counts = categorize_scores(domain_scores)
        pie_labels = list(score_counts.keys())
        pie_values = list(score_counts.values())

        fig, ax = plt.subplots(figsize=(3, 3))
        wedges, _ = ax.pie(
            pie_values,
            labels=None,
            startangle=90,
            colors=pie_colors,
            wedgeprops=dict(width=0.3, edgecolor='white')
        )

        ax.set(aspect="equal")
        ax.text(0, 0, str(sum(pie_values)), ha='center', va='center', fontsize=28, color='dimgray')
        st.pyplot(fig)

    with col2:
        domain_data = next((item for item in cookie_data if item["domain"] == selected), None)
        if domain_data:
            filtered = [domain_data]
            exp, http, sec, same = get_metrics(filtered)

            plot_stacked_bar(exp, "Expiration Duration", expiration_colors, expiration_order)
            plot_stacked_bar(http, "HttpOnly Flag", http_only_colors, http_only_order)
            plot_stacked_bar(sec, "Secure Flag", secure_colors, secure_order)
            plot_stacked_bar(same, "SameSite Attribute", samesite_colors, samesite_order)
        else:
            st.write("No cookie data available for this domain.")

elif page == "Website Checker":
    st.subheader("Check Cookies for a Specific Website")

    user_url = st.text_input("Enter a full URL (e.g., https://example.com):")
    run_check = st.button("Check Cookies")

    if run_check and user_url:
        domain = user_url.replace("https://", "").replace("http://", "").split("/")[0]

        with st.spinner("Fetching cookies..."):
            try:
                api_url = "https://three12cookieapi-1.onrender.com/scrape"
                response = requests.get(api_url, params={"domain": domain}, timeout=60)
                data = response.json()

                if "error" in data:
                    st.error(f"Error: {data['error']}")
                else:
                    st.success(f"Cookies from {domain}")
                    st.json(data["cookies"])

                    # Score and display results
                    scores = score_cookies(domain, data["cookies"])
                    st.write("Scores:", scores)

                    # Pie chart visualization
                    score_counts = categorize_scores(scores)
                    pie_labels = list(score_counts.keys())
                    pie_values = list(score_counts.values())

                    fig1, ax1 = plt.subplots(figsize=(3, 3))
                    wedges, _ = ax1.pie(
                        pie_values,
                        labels=None,
                        startangle=90,
                        colors=pie_colors,
                        wedgeprops=dict(width=0.3, edgecolor='white')
                    )
                    ax1.set(aspect="equal")
                    ax1.text(0, 0, str(sum(pie_values)), ha='center', va='center', fontsize=28, color='dimgray')
                    st.pyplot(fig1)

                    # Attribute breakdowns
                    fetched_data = [{"domain": domain, "cookies": data["cookies"]}]
                    exp, http, sec, same = get_metrics(fetched_data)
                    plot_stacked_bar(exp, "Expiration Duration", expiration_colors, expiration_order)
                    plot_stacked_bar(http, "HttpOnly Flag", http_only_colors, http_only_order)
                    plot_stacked_bar(sec, "Secure Flag", secure_colors, secure_order)
                    plot_stacked_bar(same, "SameSite Attribute", samesite_colors, samesite_order)

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")