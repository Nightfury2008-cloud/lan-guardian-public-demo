"""LAN Guardian - Network Security Demo (PUBLIC PAGE, SIMULATED DATA ONLY).

This file is the public deployment entry point. It shows what the LAN
Guardian dashboard looks like using fictional sample data only.

Hard safety rules enforced by design:

  * It never imports main.py or dashboard.py (it imports nothing from
    this project at all).
  * It never reads or writes any file: no JSON files, no backup files,
    no local reports, no environment variables, no databases.
  * It never runs operating-system commands and never opens network
    connections - no scanning, no contacting devices, nothing.
  * Every IP address, MAC address, device name, alert, scan record and
    report line is fictional. The IP addresses come from the reserved
    documentation ranges defined in RFC 5737 (192.0.2.0/24,
    198.51.100.0/24, 203.0.113.0/24), which are never used on real
    networks. MAC addresses are obvious placeholders (aa-bb-cc-...).
  * All demo state lives in Streamlit's in-memory session state; the
    "Run Demo Scan" button only changes that in-memory state.

Run it with:
    python -m streamlit run public_demo.py

Only this file is safe to publish. The local version (main.py,
dashboard.py and the JSON data files) shows your real network details
and must stay on your own computer.
"""

from datetime import datetime

import streamlit as st


# ==================================================================
# FICTIONAL SAMPLE DATA  (documentation-range IPs, placeholder MACs)
# ==================================================================

DEVICE_POOL = [
    {
        "ip": "192.0.2.1",
        "mac": "aa-bb-cc-dd-ee-01",
        "name": "Example Router (fictional)",
        "status": "KNOWN",
        "note": "On the demo trusted list.",
    },
    {
        "ip": "192.0.2.10",
        "mac": "aa-bb-cc-dd-ee-02",
        "name": "Sample Laptop (fictional)",
        "status": "KNOWN",
        "note": "On the demo trusted list.",
    },
    {
        "ip": "198.51.100.20",
        "mac": "aa-bb-cc-dd-ee-03",
        "name": "Demo Phone (fictional)",
        "status": "KNOWN",
        "note": "On the demo trusted list.",
    },
    {
        "ip": "203.0.113.50",
        "mac": "aa-bb-cc-dd-ee-04",
        "name": "Fictional Smart TV",
        "status": "KNOWN",
        "note": "On the demo trusted list.",
    },
    {
        "ip": "192.0.2.77",
        "mac": "aa-bb-cc-dd-ee-05",
        "name": "Unrecognized example device",
        "status": "UNRECOGNIZED",
        "note": "Not on the demo trusted list - an observation, never an accusation.",
    },
    {
        "ip": "198.51.100.99",
        "mac": "aa-bb-cc-dd-ee-06",
        "name": "Example guest device (fictional)",
        "status": "UNRECOGNIZED",
        "note": "Not on the demo trusted list - an observation, never an accusation.",
    },
    {
        "ip": "203.0.113.120",
        "mac": "aa-bb-cc-dd-ee-07",
        "name": "Fictional Printer",
        "status": "KNOWN",
        "note": "Appears only in the middle demo scan below.",
    },
]

# The steady six: everything except the printer.
STEADY_IPS = (
    "192.0.2.1",
    "192.0.2.10",
    "198.51.100.20",
    "203.0.113.50",
    "192.0.2.77",
    "198.51.100.99",
)

PRINTER_EVENT = {
    "id": "demo-printer-203.0.113.120",
    "type": "NEWLY_OBSERVED (simulated)",
    "ip": "203.0.113.120",
    "mac": "aa-bb-cc-dd-ee-07",
    "details": (
        "A fictional printer joined the demo network. In LAN Guardian "
        "this kind of notice is an observation to review, not an "
        "accusation - and every value here is made up for this page."
    ),
}

# The three demo scans, cycled in order by the "Run Demo Scan" button.
DEMO_SCAN_STEPS = (
    {
        "ips": STEADY_IPS + ("203.0.113.120",),
        "headline": "A fictional printer just appeared (simulated).",
        "message": (
            "Demo scan complete: 7 fictional devices observed. The "
            "printer at 203.0.113.120 is new to this demo - a notice "
            "to review, never a verdict."
        ),
        "event": "raise",
    },
    {
        "ips": STEADY_IPS,
        "headline": "The fictional printer was not seen this time (simulated).",
        "message": (
            "Demo scan complete: 6 fictional devices observed. The "
            "printer is missing from this single demo scan, and in a "
            "demo - just like in real life - that proves nothing by "
            "itself: devices sleep, leave, or are simply absent from a "
            "local cache. The simulated notice was closed with an "
            "explanation instead of being deleted."
        ),
        "event": "resolve",
    },
    {
        "ips": STEADY_IPS,
        "headline": "No changes among the steady fictional devices (simulated).",
        "message": (
            "Demo scan complete: 6 fictional devices observed, matching "
            "the demo baseline. UNRECOGNIZED still only means 'not on "
            "the demo trusted list'."
        ),
        "event": None,
    },
)

SEED_DEVICES = [dict(device) for device in DEVICE_POOL
                if device["ip"] in STEADY_IPS]

SEED_HISTORY = [
    {
        "scan": 4,
        "when": "2026-10-01 09:00 (fictional)",
        "status": "successful",
        "devices": 6,
        "detail": "Six fictional devices observed.",
    },
    {
        "scan": 3,
        "when": "2026-10-01 08:45 (fictional)",
        "status": "successful",
        "devices": 5,
        "detail": "Five fictional devices observed (the guest device was asleep).",
    },
    {
        "scan": 2,
        "when": "2026-10-01 08:30 (fictional)",
        "status": "FAILED",
        "devices": "-",
        "detail": (
            "Simulated failure - a failed scan is never counted as "
            "'zero devices', in this demo or in the real program."
        ),
    },
    {
        "scan": 1,
        "when": "2026-10-01 08:15 (fictional)",
        "status": "successful",
        "devices": 5,
        "detail": "First fictional scan of the demo story.",
    },
]

SEED_EVENTS = [
    {
        "id": "demo-unrecognized-192.0.2.77",
        "type": "UNRECOGNIZED_DEVICE (simulated)",
        "ip": "192.0.2.77",
        "mac": "aa-bb-cc-dd-ee-05",
        "first_seen": "2026-10-01 09:10 (fictional)",
        "last_seen": "2026-10-01 09:00 (fictional)",
        "count": 2,
        "details": (
            "Not on the demo trusted list. That is an observation, "
            "never proof of an attack - in real life this is usually "
            "a friend's phone or a smart-home gadget."
        ),
    },
    {
        "id": "demo-router-renamed",
        "type": "LABEL_UPDATED (simulated)",
        "ip": "192.0.2.1",
        "mac": "aa-bb-cc-dd-ee-01",
        "first_seen": "2026-10-01 08:20 (fictional)",
        "last_seen": "2026-10-01 08:20 (fictional)",
        "count": 1,
        "details": "The demo name of the fictional router was updated.",
        "resolved_at": "2026-10-01 08:25 (fictional)",
        "resolution": (
            "Demo explanation: nothing was wrong - the fictional owner "
            "renamed the device. Resolved notices are kept with their "
            "explanation, never silently deleted."
        ),
    },
]

SEED_LAST_SCAN = "2026-10-01 09:00 (fictional)"


# ==================================================================
# PURE DEMO HELPERS  (no I/O of any kind)
# ==================================================================

def select_devices(ips):
    """Fictional devices for the given demo addresses, in pool order."""
    wanted = set(ips)
    return [dict(device) for device in DEVICE_POOL if device["ip"] in wanted]


def count_known(devices):
    """How many demo devices are on the demo trusted list."""
    return sum(1 for device in devices
               if device["status"] in ("KNOWN", "KNOWN AT NEW IP"))


def active_alerts(events):
    """Number of simulated notices that are still active."""
    return sum(1 for event in events if "resolved_at" not in event)


def raise_demo_event(events, event, seen):
    """Activate a simulated notice (or bump it if it already exists)."""
    for existing in events:
        if existing["id"] == event["id"]:
            existing["count"] += 1
            existing["last_seen"] = seen
            existing.pop("resolved_at", None)
            existing.pop("resolution", None)
            return events
    events.insert(0, {
        "id": event["id"],
        "type": event["type"],
        "ip": event["ip"],
        "mac": event["mac"],
        "first_seen": seen,
        "last_seen": seen,
        "count": 1,
        "details": event["details"],
    })
    return events


def resolve_demo_event(events, event_id, resolution, when):
    """Close an active simulated notice, keeping its explanation."""
    for existing in events:
        if existing["id"] == event_id and "resolved_at" not in existing:
            existing["resolved_at"] = when
            existing["resolution"] = resolution
    return events


def device_rows(devices):
    """Table rows for the fictional device list."""
    return [
        {
            "IP (documentation range)": device["ip"],
            "MAC (fictional)": device["mac"],
            "Status": device["status"],
            "Device name (fictional)": device["name"],
            "Note": device["note"],
        }
        for device in devices
    ]


def history_rows(history):
    """Table rows for the simulated scan history (newest first)."""
    return [
        {
            "Scan": f"#{record['scan']}",
            "When": record["when"],
            "Status": record["status"],
            # All values as text: the FAILED row uses "-", and a mixed
            # int/str column is rejected by the Arrow table converter.
            "Devices": str(record["devices"]),
            "Detail": record["detail"],
        }
        for record in history
    ]


def event_rows(events):
    """Table rows for the simulated notices."""
    return [
        {
            "Status": "RESOLVED" if "resolved_at" in event else "ACTIVE",
            "Type": event["type"],
            "IP": event["ip"],
            "MAC": event["mac"],
            "First seen": event["first_seen"],
            "Last seen": event.get("last_seen", "-"),
            "Times seen": event["count"],
        }
        for event in events
    ]


def feature_card_html(icon, title, body):
    """Self-contained feature card for the landing page.

    Pure string formatting - no I/O, no session state. Colours are set
    explicitly so the card stays readable in light and dark themes.
    """
    return (
        '<div class="lg-card">'
        f'<div class="lg-card-icon" aria-hidden="true">{icon}</div>'
        f"<h3>{title}</h3>"
        f"<p>{body}</p>"
        "</div>"
    )


def build_demo_report(devices, history, events):
    """Build the example report entirely in memory (never saved)."""
    lines = []

    def line(text=""):
        lines.append(text)

    line("=" * 70)
    line("LAN GUARDIAN - EXAMPLE SECURITY REPORT")
    line("(SIMULATED - EVERY VALUE ON THIS PAGE IS FICTIONAL)")
    line("=" * 70)
    line(f"Generated:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    line("               (demo run, held in memory only)")
    line("Data source:   fictional sample data - no network activity")
    line("Disk writes:   none - this text is displayed, never saved")
    line()

    line("-- Observed devices (fictional) " + "-" * 37)
    for device in devices:
        line(f"  {device['ip']:<16} {device['mac']}  "
             f"{device['status']:<13} {device['name']}")
    line(f"  Total: {len(devices)} simulated devices, "
         f"{count_known(devices)} known, "
         f"{len(devices) - count_known(devices)} unrecognized.")
    line()

    line("-- Simulated scan history (newest first) " + "-" * 28)
    for record in history:
        line(f"  #{record['scan']:<3} {record['when']:<32} "
             f"{record['status']:<12} devices: {record['devices']}")
    line()

    line("-- Simulated security notices " + "-" * 40)
    for event in events:
        state = "RESOLVED" if "resolved_at" in event else "ACTIVE  "
        line(f"  [{state}] {event['type']} | IP {event['ip']} | "
             f"seen {event['count']}x")
        line(f"           {event['details']}")
        if "resolution" in event:
            line(f"           Resolution: {event['resolution']}")
    line()

    line("-- How to read this report " + "-" * 43)
    line("  * UNRECOGNIZED means 'not on the trusted list' -")
    line("    it never means 'attacker'.")
    line("  * A device missing from a single scan proves nothing.")
    line("  * A FAILED scan is an error, not an empty network.")
    line("  * This is sample output. The local version of LAN Guardian")
    line("    produces the same sections from your own network.")
    line("=" * 70)
    return "\n".join(lines)


# ==================================================================
# DEMO STATE (in-memory, session only - never touches disk)
# ==================================================================

def init_demo_state():
    """Create the fictional starting state in session memory."""
    if "demo_devices" not in st.session_state:
        st.session_state.demo_devices = [dict(d) for d in SEED_DEVICES]
        st.session_state.demo_history = [dict(h) for h in SEED_HISTORY]
        st.session_state.demo_events = [dict(e) for e in SEED_EVENTS]
        st.session_state.demo_scans_run = 0
        st.session_state.demo_last_scan = SEED_LAST_SCAN
        st.session_state.demo_message = ""


def run_demo_scan():
    """Advance the demo. Changes in-memory state ONLY: no commands,
    no network, no files."""
    steps = DEMO_SCAN_STEPS
    step = steps[st.session_state.demo_scans_run % len(steps)]
    st.session_state.demo_scans_run += 1

    run_number = st.session_state.demo_scans_run
    when = (datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + f" (demo run #{run_number})")

    devices = select_devices(step["ips"])
    st.session_state.demo_devices = devices

    history = st.session_state.demo_history
    next_scan = history[0]["scan"] + 1 if history else 1
    history.insert(0, {
        "scan": next_scan,
        "when": when,
        "status": "successful",
        "devices": len(devices),
        "detail": step["headline"],
    })
    del history[12:]

    events = st.session_state.demo_events
    if step["event"] == "raise":
        raise_demo_event(events, PRINTER_EVENT, when)
    elif step["event"] == "resolve":
        resolve_demo_event(
            events,
            PRINTER_EVENT["id"],
            "Demo explanation: the fictional printer is asleep for this "
            "step of the story. A device missing from one scan proves "
            "nothing - the local version likewise requires 2 "
            "consecutive successful scans before even mentioning a "
            "possible disappearance, and then it explains rather than "
            "accuses.",
            when,
        )

    st.session_state.demo_last_scan = when
    st.session_state.demo_message = step["message"]


# ==================================================================
# PAGE
# ==================================================================

def run_demo():
    st.set_page_config(
        page_title="LAN Guardian — Network Security Demo",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .lg-demo-banner {
            background: #7f1d1d;
            color: #fef2f2;
            padding: 14px 20px;
            border-radius: 8px;
            border: 1px solid #fca5a5;
            text-align: center;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.6px;
            margin-bottom: 6px;
        }
        .lg-demo-title {
            margin-bottom: 0;
        }
        .lg-note {
            font-size: 0.85rem;
            color: #64748b;
            border-left: 3px solid #cbd5e1;
            padding-left: 10px;
            margin-top: 6px;
        }

        /* ---------- landing page ---------- */
        .lg-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #1d4ed8 100%);
            color: #f8fafc;
            border-radius: 14px;
            padding: clamp(22px, 4vw, 44px);
            margin: 4px 0 16px 0;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
        }
        .lg-hero h1 {
            color: #f8fafc;
            font-size: clamp(1.8rem, 3.6vw, 2.7rem);
            margin: 0 0 6px 0;
            line-height: 1.15;
        }
        .lg-kicker {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 2px;
            color: #93c5fd;
            margin: 0 0 10px 0;
        }
        .lg-tagline {
            color: #dbeafe;
            font-size: clamp(1.05rem, 2vw, 1.35rem);
            font-weight: 600;
            margin: 0 0 10px 0;
        }
        .lg-hero-sub {
            color: #cbd5e1;
            font-size: 0.98rem;
            line-height: 1.6;
            margin: 0;
            max-width: 72ch;
        }
        .lg-sim-notice {
            background: #fffbeb;
            color: #78350f;
            border: 1px solid #fcd34d;
            border-left: 6px solid #d97706;
            border-radius: 10px;
            padding: 14px 16px;
            margin: 4px 0 16px 0;
            font-size: 0.95rem;
            line-height: 1.55;
        }
        .lg-sim-notice strong {
            color: #92400e;
            letter-spacing: 0.5px;
        }
        .lg-card {
            background: #ffffff;
            color: #0f172a;
            border: 1px solid #e2e8f0;
            border-top: 4px solid #2563eb;
            border-radius: 12px;
            padding: 18px;
            height: 100%;
            box-sizing: border-box;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.10);
        }
        .lg-card h3 {
            color: #0f172a;
            font-size: 1.05rem;
            margin: 0 0 8px 0;
        }
        .lg-card p {
            color: #334155;
            font-size: 0.92rem;
            line-height: 1.6;
            margin: 0;
        }
        .lg-card-icon {
            font-size: 1.5rem;
            line-height: 1;
            margin-bottom: 8px;
        }
        </style>
        <div class="lg-demo-banner">PUBLIC DEMO — ALL DATA IS SIMULATED</div>
        """,
        unsafe_allow_html=True,
    )

    # Programmatic jump: the landing-page button sets this flag and
    # reruns. The flag is applied HERE - before the radio is created -
    # because a widget-backed session key may only be set before that
    # widget is instantiated.
    if "lg_go_demo" in st.session_state and st.session_state["lg_go_demo"]:
        st.session_state["lg_section"] = "Overview"
        st.session_state["lg_go_demo"] = False

    st.sidebar.title("Demo navigation")
    section = st.sidebar.radio(
        "Sections",
        [
            "Landing",
            "Overview",
            "Scan history",
            "Security events",
            "Example report",
            "About the local version",
        ],
        key="lg_section",
    )

    st.sidebar.markdown(
        "---\n"
        "**What this page is**\n\n"
        "A public showcase built from fictional sample data.\n\n"
        "**What it never does**\n\n"
        "- Never runs operating-system commands\n"
        "- Never opens network connections\n"
        "- Never reads or writes files\n"
        "- Never collects or sends anything\n\n"
        "Reset the demo by reloading the page."
    )

    init_demo_state()

    if section == "Landing":
        render_landing()
    else:
        # Every other section keeps the original page header.
        render_page_header()
        if section == "Overview":
            render_overview()
        elif section == "Scan history":
            render_history()
        elif section == "Security events":
            render_events()
        elif section == "Example report":
            render_report()
        else:
            render_about()

    st.markdown(
        "<p class='lg-note'>Fictional data only: IP addresses are from "
        "the RFC 5737 documentation ranges, MAC addresses are "
        "placeholders (aa-bb-cc-...), and all names are invented for "
        "this demo.</p>",
        unsafe_allow_html=True,
    )


def render_page_header():
    """Header shown above every section except the landing page."""
    st.markdown(
        "<h1 class='lg-demo-title'>LAN Guardian — "
        "Network Security Demo</h1>",
        unsafe_allow_html=True,
    )
    st.caption(
        "A guided tour of the LAN Guardian interface. Every IP address, "
        "MAC address, device name, alert and scan below is fictional "
        "sample data held only in this browser session."
    )


def render_landing():
    """Landing page: project intro, simulation notice, feature cards."""
    st.markdown(
        """
        <div class="lg-hero">
            <div class="lg-kicker">EDUCATIONAL CYBERSECURITY PROJECT</div>
            <h1>LAN Guardian</h1>
            <p class="lg-tagline">Understand changes on your local network.</p>
            <p class="lg-hero-sub">
                See which devices are present on a local network, notice
                when something changes, and read a clear explanation of
                what happened - calmly, and without guesswork.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation only: it pre-seeds the sidebar radio (via the flag
    # handled at the top of run_demo) and reruns once.
    if st.button("Open the interactive demo", type="primary",
                 key="lg_open_demo"):
        st.session_state["lg_go_demo"] = True
        st.rerun()

    st.caption(
        "Jumps to the interactive demo (Overview section). Navigation "
        "only - the button runs no commands, opens no network "
        "connections and writes no files."
    )

    st.markdown(
        """
        <div class="lg-sim-notice">
            <strong>PUBLIC SIMULATION</strong> &mdash; every device, IP
            address, MAC address, scan result, alert and timestamp on
            this page is fictional sample data. This page never scans
            any visitor's network: it runs no operating-system commands,
            contacts nothing, and reads or writes no files. Live
            monitoring exists only in the separate local version, and
            only on its own computer.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Why monitoring matters")
    st.markdown(
        "Most home, campus and office networks quietly fill up with "
        "phones, laptops, consoles, cameras and smart-home gadgets, and "
        "devices join and leave all the time - so an unexpected arrival "
        "is easy to miss. Monitoring your own network is about "
        "**knowing what normal looks like**: when the usual devices are "
        "familiar, a new or changed entry stands out as a question "
        "worth checking - calmly and with evidence - rather than as a "
        "panic. This project deliberately teaches that habit: observe "
        "first, then decide."
    )

    st.markdown("### What LAN Guardian does")
    columns = st.columns(3)
    with columns[0]:
        st.markdown(feature_card_html(
            "🔎",
            "Device Visibility",
            "Every observed device is listed with its IP address, MAC "
            "address and a friendly name. Entries on the trusted list "
            "are marked <strong>KNOWN</strong>; anything else is simply "
            "<strong>UNRECOGNIZED</strong> - a prompt to look, never a "
            "label of guilt.",
        ), unsafe_allow_html=True)
    with columns[1]:
        st.markdown(feature_card_html(
            "🔄",
            "Change Monitoring",
            "Each observation is compared with a saved baseline, so new "
            "arrivals, departures and address changes are reported in "
            "plain language. A device must be absent from two "
            "consecutive successful scans before a possible "
            "disappearance is even mentioned.",
        ), unsafe_allow_html=True)
    with columns[2]:
        st.markdown(feature_card_html(
            "🗂️",
            "Security Event History",
            "Notices are recorded with their full story: first seen, "
            "times seen, and how they were resolved. Resolved events "
            "keep their explanation instead of vanishing, so the "
            "history stays honest and reviewable.",
        ), unsafe_allow_html=True)

    st.markdown("### About the Project")
    st.markdown(
        "**LAN Guardian** is an educational cybersecurity project: a "
        "small, readable program that demonstrates how defensive "
        "network monitoring works on a personal computer. The local "
        "version is built from beginner-friendly Python - a "
        "standard-library command-line program plus a Streamlit "
        "dashboard - so every part can be opened, run and understood "
        "while you study it.\n\n"
        "One principle runs through the whole project: **an unfamiliar "
        "device is not automatically malicious.** A device that is not "
        "on your trusted list is most often a guest's phone, a new "
        "smart television or a neighbour's gadget. LAN Guardian "
        "reports observations with explanations and leaves every "
        "judgement to the person operating it.\n\n"
        "Live monitoring of a real network is available only in the "
        "**separate local version**, which runs on your own computer - "
        "see *About the local version* in the sidebar. This public "
        "page exists to demonstrate the interface with fictional data."
    )
    st.caption(
        "Explore next (sidebar): Overview · Scan history · Security "
        "events · Example report · About the local version."
    )


def render_overview():
    st.subheader("Overview")

    # The scan button sits ABOVE everything that displays demo state:
    # a Streamlit button click IS the rerun, so nothing below re-runs
    # afterwards. Advancing the demo first keeps the cards, message and
    # table consistent with the scan that was just clicked.
    if st.button("Run Demo Scan", type="primary"):
        run_demo_scan()

    st.caption(
        "This button only changes the fictional demo data held in this "
        "browser session. It runs no operating-system commands, opens "
        "no network connections and writes no files."
    )

    devices = st.session_state.demo_devices
    events = st.session_state.demo_events

    columns = st.columns(4)
    columns[0].metric("Simulated devices", len(devices))
    columns[1].metric("Known devices", count_known(devices))
    columns[2].metric(
        "Simulated alerts", active_alerts(events),
        help="Active fictional notices - still-open items in the demo story.",
    )
    columns[3].metric(
        "Last simulated scan", st.session_state.demo_last_scan)

    if st.session_state.demo_message:
        st.info(st.session_state.demo_message)

    st.divider()

    st.markdown("#### Observed devices (fictional)")
    st.dataframe(
        device_rows(devices),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        """
        **Status guide**

        | Status | What it means (demo) |
        |---|---|
        | `KNOWN` | On the fictional trusted list. |
        | `UNRECOGNIZED` | Not on the fictional trusted list. An observation to review - **never** an accusation. |
        """
    )
    st.markdown(
        "<p class='lg-note'>The real program additionally explains that "
        "a local cache is an incomplete view of a network: a device "
        "can be perfectly fine and simply not appear. This demo shows "
        "the same calm, explanatory tone with made-up data.</p>",
        unsafe_allow_html=True,
    )


def render_history():
    st.subheader("Scan history (simulated)")
    st.caption(
        "Fictional scan records, newest first. The FAILED row shows how "
        "an error is reported honestly: a failed scan is never shown as "
        "'zero devices'."
    )

    st.dataframe(
        history_rows(st.session_state.demo_history),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "<p class='lg-note'>Every row above is invented for this demo. "
        "In the local version the same table holds your own computer's "
        "saved observations.</p>",
        unsafe_allow_html=True,
    )


def render_events():
    st.subheader("Security events (simulated)")
    st.caption(
        "Fictional notices with explanations. Active items are shown "
        "first; resolved items are kept with their resolution instead "
        "of being deleted."
    )

    events = st.session_state.demo_events
    st.dataframe(event_rows(events), width="stretch", hide_index=True)

    active = [e for e in events if "resolved_at" not in e]
    resolved = [e for e in events if "resolved_at" in e]

    if active:
        st.markdown("#### Active (simulated)")
        for event in active:
            with st.expander(
                f"ACTIVE — {event['type']} · IP {event['ip']}"
            ):
                st.write(event["details"])
                st.caption(
                    f"First seen {event['first_seen']} · last seen "
                    f"{event.get('last_seen', '-')} · seen "
                    f"{event['count']} time(s) — all fictional."
                )

    if resolved:
        st.markdown("#### Resolved (simulated)")
        for event in resolved:
            with st.expander(
                f"RESOLVED — {event['type']} · IP {event['ip']}"
            ):
                st.write(event["details"])
                st.write(event.get("resolution", ""))
                st.caption(
                    f"First seen {event['first_seen']} · resolved "
                    f"{event.get('resolved_at', '-')} — fictional."
                )

    st.markdown(
        "<p class='lg-note'>Unrecognized devices and missing entries "
        "are never presented as proof of an attack - here or in the "
        "real program.</p>",
        unsafe_allow_html=True,
    )


def render_report():
    st.subheader("Example security report")
    st.caption(
        "Built in memory from the fictional demo data and shown below. "
        "It is never written to disk and never uploaded anywhere."
    )

    text = build_demo_report(
        st.session_state.demo_devices,
        st.session_state.demo_history,
        st.session_state.demo_events,
    )
    st.code(text, language="text")

    st.markdown(
        "<p class='lg-note'>This is what the report section of the "
        "local version looks like - produced there from your own "
        "network's saved observations and saved as "
        "<b>security_report.txt</b> in the project folder only.</p>",
        unsafe_allow_html=True,
    )


def render_about():
    st.subheader("About the local version")

    st.markdown(
        """
        ### Live LAN monitoring lives in the **local** version

        This public page is a showcase with fictional sample data.
        Actual monitoring of your own network happens only on your own
        computer, with the original LAN Guardian program in this
        project:

        ```powershell
   cd path/to/LAN-Guardian

        # command-line program (ten-option menu)
        python main.py

        # local web dashboard (same look as this demo, real data)
        python -m streamlit run dashboard.py
        ```

        The local version:

        - reads **your** computer's local network configuration and
          saved observations to build its tables - this public demo
          does none of that;
        - keeps every file (`trusted_devices.json`,
          `device_baseline.json`, `scan_history.json`,
          `security_events.json`, `security_report.txt`) in its own
          project folder and never transmits them;
        - requires your confirmation before changing trusted entries,
          replacing the baseline or removing anything, and writes
          timestamped backups first.

        ### What this public demo never does

        | Guarantee | Detail |
        |---|---|
        | No operating-system commands | The scan button only updates in-memory demo state. |
        | No network activity | Nothing on your machine or network is contacted; no external services are used. |
        | No file access | No JSON files, backups, reports, environment variables or databases are read or written. |
        | No local program imports | This file imports only `streamlit` and the Python standard library (`datetime`). |
        | No real data | Every IP, MAC, name, alert and timestamp is fictional; IPs are from RFC 5737 documentation ranges. |
        | Session-only state | Reload the page and the demo resets to its fictional starting point. |

        ### Deploying safely

        Only `public_demo.py` is meant to be published. The local files
        (`main.py`, `dashboard.py` and the JSON data) can reveal your
        real network details - keep them on your own computer.
        """
    )


# Streamlit runs this file as __main__; importing it does nothing.
if __name__ == "__main__":
    run_demo()
