import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ==========================================
# TRUSTLENS PROJECT TIMELINE
# ==========================================

tasks = [
    ("Literature Survey",
     "2026-01-05", "2026-01-18"),

    ("Requirement Analysis",
     "2026-01-19", "2026-02-01"),

    ("Dataset Collection",
     "2026-02-02", "2026-02-15"),

    ("Data Preprocessing",
     "2026-02-16", "2026-03-01"),

    ("OCR Module Development",
     "2026-03-02", "2026-03-15"),

    ("Image Feature Extraction",
     "2026-03-16", "2026-03-29"),

    ("Feature Fusion",
     "2026-03-30", "2026-04-05"),

    ("XGBoost Model Training",
     "2026-04-06", "2026-04-19"),

    ("Model Testing & Evaluation",
     "2026-04-20", "2026-05-03"),

    ("Trust Score & Risk Analysis",
     "2026-05-04", "2026-05-10"),

    ("PDF Report Generation",
     "2026-05-11", "2026-05-17"),

    ("Web Interface Development",
     "2026-05-18", "2026-05-31"),

    ("System Integration",
     "2026-06-01", "2026-06-14"),

    ("Final Testing",
     "2026-06-15", "2026-06-28"),

    ("Documentation & Final Report",
     "2026-06-29", "2026-07-12"),

    ("Final Presentation",
     "2026-07-13", "2026-07-19")
]

# ==========================================
# Convert Dates
# ==========================================

start_dates = [
    datetime.strptime(task[1], "%Y-%m-%d")
    for task in tasks
]

end_dates = [
    datetime.strptime(task[2], "%Y-%m-%d")
    for task in tasks
]

# Calculate duration
durations = [
    (end - start).days
    for start, end in zip(start_dates, end_dates)
]

# ==========================================
# Create Gantt Chart
# ==========================================

fig, ax = plt.subplots(figsize=(14, 9))

for i, (task, start, end) in enumerate(tasks):

    start_date = datetime.strptime(start, "%Y-%m-%d")

    ax.barh(
        i,
        durations[i],
        left=start_date,
        height=0.6
    )

# ==========================================
# Task Names
# ==========================================

ax.set_yticks(range(len(tasks)))

ax.set_yticklabels(
    [task[0] for task in tasks]
)

# Reverse order
ax.invert_yaxis()

# ==========================================
# Date Formatting
# ==========================================

ax.xaxis.set_major_locator(
    mdates.MonthLocator()
)

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%b %Y")
)

plt.xticks(rotation=45)

# ==========================================
# Labels
# ==========================================

plt.title(
    "TRUSTLENS - AI Digital Payment Receipt Verification System",
    fontsize=16
)

plt.xlabel("Timeline")

plt.ylabel("Project Activities")

plt.grid(
    axis="x",
    linestyle="--",
    alpha=0.5
)

plt.tight_layout()

# ==========================================
# Save Image
# ==========================================

plt.savefig(
    "TRUSTLENS_Gantt_Chart.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Gantt Chart generated successfully!")
print("Saved as: TRUSTLENS_Gantt_Chart.png")