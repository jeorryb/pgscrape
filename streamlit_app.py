#!/usr/bin/env python3
"""
Perfect Game Team Scraper — Streamlit UI

Paste a team URL or ID, optionally sign in, then scrape and download CSV
named after the team.
"""

import logging
import os
import tempfile

import streamlit as st

from pg_scraper import (
    PerfectGameScraper,
    normalize_team_input,
    sanitize_filename,
)

# Reduce log noise in the app
logging.getLogger("pg_scraper").setLevel(logging.WARNING)

st.set_page_config(
    page_title="Perfect Game Team Scraper",
    page_icon="⚾",
    layout="centered",
)

st.title("⚾ Perfect Game Team Scraper")
st.caption("Paste a team page URL or team ID to scrape roster and stats to CSV.")

url_or_id = st.text_input(
    "Team URL or ID",
    placeholder="e.g. https://www.perfectgame.org/PGBA/Team/default.aspx?orgid=11923&orgteamid=264258&team=1056361&year=2026 or 1056361",
    help="Full PGBA/Events URL or numeric team ID (e.g. 1056361).",
)

with st.expander("Optional: Perfect Game login"):
    username = st.text_input("Email", key="username", placeholder="your@email.com")
    password = st.text_input("Password", type="password", key="password")

if st.button("Scrape team", type="primary"):
    if not url_or_id or not url_or_id.strip():
        st.error("Please enter a team URL or team ID.")
        st.stop()

    team_id, team_url = normalize_team_input(url_or_id.strip())
    if not team_url:
        st.error("Could not parse team URL or ID. Use a full Perfect Game team page URL or a numeric team ID.")
        st.stop()

    with st.spinner("Scraping team and player profiles…"):
        scraper = PerfectGameScraper(
            username=username.strip() or None,
            password=password or None,
        )
        players, team_name = scraper.scrape_team(team_url)

    if not players:
        st.error("No player data found. Check the URL and try again. Some pages require login.")
        st.stop()

    # Output filename: team name or team_ID
    safe_name = sanitize_filename(team_name) if team_name else None
    filename = f"{safe_name}.csv" if safe_name else f"team_{team_id}.csv"

    # Write CSV to a temp file so we can reuse the scraper's save logic
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        scraper.save_to_csv(players, f.name)
        path = f.name
    with open(path, "rb") as fp:
        csv_bytes = fp.read()
    try:
        os.unlink(path)
    except Exception:
        pass

    st.success(f"Scraped **{len(players)}** players → `{filename}`")

    st.dataframe(players[:10], use_container_width=True)
    if len(players) > 10:
        st.caption(f"Showing first 10 of {len(players)} players.")

    st.download_button(
        "Download CSV",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        type="primary",
    )
