"""
Purpose : Store the team-name and venue-name fix dictionaries.
          Franchise renames over the years mean the same team appears
          under different names. We map old names → current names.
          Venue spellings also vary; we map them to a canonical form.
Reads   : nothing (pure data dictionaries)
Writes  : nothing
How to run: imported by clean_matches.py and clean_deliveries.py

HOW TO USE:
  Run inspect_raw_data.py first.
  Copy the printed distinct team/venue names into the maps below.
  The key is the name AS IT APPEARS in the CSV.
  The value is the name you WANT in the database.
  If a name is already correct, you do NOT need to list it here.

IMPORTANT:
  Do NOT merge different franchises.
  e.g. Deccan Chargers and Sunrisers Hyderabad are different teams — keep both.
  Only rename within the same franchise history.
"""

# ---------------------------------------------------------------------------
# TEAM NAME MAP  — verified against real CSV (inspect_raw_data.py output)
# Key   = raw name from CSV
# Value = canonical name we store in the database
# ---------------------------------------------------------------------------
# RULE: only rename within the same franchise history.
# Different franchises (e.g. Deccan Chargers vs Sunrisers Hyderabad) stay separate.
TEAM_NAME_MAP: dict[str, str] = {
    # Delhi franchise rename (2019): Delhi Daredevils → Delhi Capitals
    "Delhi Daredevils": "Delhi Capitals",

    # Punjab franchise rename (2021): Kings XI Punjab → Punjab Kings
    "Kings XI Punjab": "Punjab Kings",

    # Bangalore franchise rename: both spellings exist in the real CSV
    # We pick the newer official name "Bengaluru" as canonical
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",

    # Rising Pune franchise: two spellings exist in the real CSV
    "Rising Pune Supergiants": "Rising Pune Supergiant",

    # NOTE: The following are intentionally NOT merged — different franchises:
    # - Deccan Chargers  (2008–2012)
    # - Sunrisers Hyderabad (2013–present)
    # - Gujarat Lions  (2016–2017)
    # - Gujarat Titans (2022–present)
}


# ---------------------------------------------------------------------------
# VENUE NAME MAP  — verified against real CSV (inspect_raw_data.py output)
# Key   = raw venue/city name from CSV (every variant found in the data)
# Value = canonical venue name we store in the database
# ---------------------------------------------------------------------------
VENUE_NAME_MAP: dict[str, str] = {
    # Wankhede Stadium, Mumbai
    "Wankhede Stadium, Mumbai":     "Wankhede Stadium",

    # M. Chinnaswamy Stadium, Bangalore — three spellings in the data
    "M Chinnaswamy Stadium":            "M. Chinnaswamy Stadium",
    "M Chinnaswamy Stadium, Bengaluru": "M. Chinnaswamy Stadium",
    "M.Chinnaswamy Stadium":            "M. Chinnaswamy Stadium",

    # MA Chidambaram Stadium, Chennai — three spellings
    "MA Chidambaram Stadium, Chepauk":          "MA Chidambaram Stadium",
    "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium",

    # Eden Gardens, Kolkata
    "Eden Gardens, Kolkata": "Eden Gardens",

    # Feroz Shah Kotla → now Arun Jaitley Stadium (renamed 2019)
    "Feroz Shah Kotla":          "Arun Jaitley Stadium",
    "Arun Jaitley Stadium, Delhi": "Arun Jaitley Stadium",

    # Rajiv Gandhi International Stadium, Hyderabad — three spellings
    "Rajiv Gandhi International Stadium, Uppal":          "Rajiv Gandhi International Stadium",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium",

    # Punjab Cricket Association IS Bindra Stadium, Mohali — three spellings
    "Punjab Cricket Association IS Bindra Stadium, Mohali":           "Punjab Cricket Association IS Bindra Stadium",
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh": "Punjab Cricket Association IS Bindra Stadium",
    "Punjab Cricket Association Stadium, Mohali":                     "Punjab Cricket Association IS Bindra Stadium",

    # Himachal Pradesh Cricket Association Stadium, Dharamsala
    "Himachal Pradesh Cricket Association Stadium, Dharamsala": "Himachal Pradesh Cricket Association Stadium",

    # Sawai Mansingh Stadium, Jaipur
    "Sawai Mansingh Stadium, Jaipur": "Sawai Mansingh Stadium",

    # Maharashtra Cricket Association Stadium, Pune
    "Maharashtra Cricket Association Stadium, Pune": "Maharashtra Cricket Association Stadium",

    # Dr DY Patil Sports Academy, Mumbai
    "Dr DY Patil Sports Academy, Mumbai": "Dr DY Patil Sports Academy",

    # Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam": "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",

    # Sardar Patel Stadium → now Narendra Modi Stadium (renamed 2020)
    "Sardar Patel Stadium, Motera": "Narendra Modi Stadium, Ahmedabad",

    # Zayed Cricket Stadium, Abu Dhabi → now Sheikh Zayed Stadium
    "Zayed Cricket Stadium, Abu Dhabi": "Sheikh Zayed Stadium",

    # Dubai International Cricket Stadium = Dubai (city used as venue name in some rows)
    # We leave both as-is since they are different physical grounds.

    # Brabourne Stadium, Mumbai
    "Brabourne Stadium, Mumbai": "Brabourne Stadium",

    # Maharaja Yadavindra Singh International Cricket Stadium — two city name spellings
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh": "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
}

