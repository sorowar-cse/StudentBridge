"""StudentBridge v4. Each cloud session owns its Auth adapter; only public data is cached."""

from datetime import datetime, timezone
from decimal import Decimal
from html import escape
from pathlib import Path
import math
import os
import time

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from studentbridge.agent import FinanceAgent
from studentbridge.broker import SandboxBroker
from studentbridge.documents import (
    audit_statement,
    comparison_statement,
    conversion_statement,
    planning_invoice,
    transfer_receipt,
    university_statement,
)
from studentbridge.fx import FXService
from studentbridge.i18n import LANGUAGES, Translator
from studentbridge.llm import JSONClient, ModelConfig
from studentbridge.money import FinanceError, major, rounded, decimal
from studentbridge.risk import RiskEngine
from studentbridge.store import Store
from studentbridge.cloud import CloudStore, CloudBroker
from studentbridge.profile_ui import profile_page, forecast_page, account_page
from studentbridge.personal_assistant import personal_fee_answer, render_personal_fee
from studentbridge.team import members, profile_image
from studentbridge.ui_hints import hint
from studentbridge.university import UniversityCatalog, budget_scenario, due_plan

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="StudentBridge", page_icon="🌉", layout="wide")
st.markdown(
    "<style>" + (ROOT / "assets/theme.css").read_text() + "</style>", unsafe_allow_html=True
)

# Stable codes are separate from translated labels, including navigation and currencies.
if "language" not in st.session_state:
    st.session_state.language = "en"
if "settings" not in st.session_state:
    st.session_state.settings = {
        "fx_mode": "demo" if os.getenv("STUDENTBRIDGE_FX_MODE") == "demo" else "live",
        "provider": os.getenv("STUDENTBRIDGE_AI_PROVIDER", "offline")
        if os.getenv("STUDENTBRIDGE_AI_PROVIDER", "offline") in {"groq", "ollama", "offline"}
        else "offline",
        "cloud_consent": False,
        "models": {
            "groq": {
                "planner": os.getenv("PLANNER_MODEL", "openai/gpt-oss-20b"),
                "reviewer": os.getenv("REVIEWER_MODEL", "openai/gpt-oss-120b"),
            },
            "ollama": {
                "planner": os.getenv("OLLAMA_PLANNER_MODEL", "qwen3:4b"),
                "reviewer": os.getenv("OLLAMA_REVIEWER_MODEL", "gemma3:4b"),
            },
        },
    }

with st.sidebar:
    st.markdown("<div class=\"sb-brand\">StudentBridge</div>", unsafe_allow_html=True)
    st.selectbox("Language", list(LANGUAGES), format_func=LANGUAGES.get, key="language")
t = Translator(st.session_state.language)
NAV = [
    "dashboard",
    "profile",
    "forecast",
    "assistant",
    "converter",
    "planner",
    "transfers",
    "wallet",
    "account",
    "developer",
    "guide",
]
with st.sidebar:
    page = st.radio(t("navigation"), NAV, format_func=t, key="nav")
    st.caption(t("release"))


def go(destination):
    st.session_state.nav = destination


@st.cache_resource
def resources(directory):
    return Store(directory), RiskEngine(), UniversityCatalog()


@st.cache_data(ttl=3600, show_spinner=False)
def currency_catalog(mode):
    return FXService(mode).currencies()


@st.cache_resource
def shared_resources():
    return RiskEngine(), UniversityCatalog()


def clear_session():
    language = st.session_state.language
    st.session_state.clear()
    st.session_state.language = language


def accept_login(new_token):
    # A new identity must not inherit old quotes, PDFs, budgets or cloud consent.
    language = st.session_state.language
    cloud_state = st.session_state.get("_cloud_auth") if backend == "supabase" else None
    st.session_state.clear()
    st.session_state.language = language
    if cloud_state is not None:
        st.session_state._cloud_auth = cloud_state
    st.session_state.token = new_token


st.markdown(
    f'<div class="sb-hero"><div class="sb-kicker">{escape(t("brand_line"))}</div>'
    f"<h1>{escape(t("hero"))}</h1><p>{escape(t("hero_sub"))}</p></div>",
    unsafe_allow_html=True,
)
st.markdown(f'<div class="sb-safety">{escape(t("simulation"))}</div>', unsafe_allow_html=True)


def display_error(exc):
    st.error(t.error(exc))
    with st.expander(t("technical_details")):
        st.code(str(exc), language=None)


def select_currency(label, codes, default, key):
    return st.selectbox(
        t(label),
        codes,
        index=codes.index(default) if default in codes else 0,
        format_func=t.currency_label,
        key=key,
    )


def pdf_download(label, data, name, key):
    st.download_button(t(label), data, file_name=name, mime="application/pdf", key=key)


def reference(ref):
    kind = "live" if ref["mode"] == "live" else "offline"
    st.caption(f"{t("rate_source")}: {t(kind)} · {t("reference_date")}: {ref["as_of"]}")
    st.caption(t("reference_note") if kind == "live" else t("illustrative_note"))


def programme_card(record):
    st.write(f"**{record["university"]} · {record["programme"]}**")
    st.caption(
        f"{record["city"]}, {t(record["country"])} · {t(record["level"])} · {record["language"]}"
    )
    if record["fee"] is None:
        st.info(t("manual_fee"))
    else:
        period_key = (
            "programme_period" if record["fee_period"] == "programme" else record["fee_period"]
        )
        st.write(
            f"{t("reference_fee")}: **{record["fee"]} {record["currency"]} / {t(period_key)}**"
        )
    st.caption(t("checked") + ": " + record["checked_on"])
    st.link_button(t("source_link"), record["source_url"])
    with st.expander(t("original_source")):
        st.write(record["notes"])
        st.caption(t("source_year") + ": " + record["source_year"])


def provider_table(options):
    st.dataframe(
        [
            {
                t("provider"): r["provider"],
                t("spend"): f"{major(r["spend_minor"], r["source"])} {r["source"]}",
                t("fee_included"): f"{major(r["fee_minor"], r["source"])} {r["source"]}",
                t("received"): f"{major(r["receive_minor"], r["target"])} {r["target"]}",
                t("minutes_estimate"): r["minutes"],
            }
            for r in options
        ],
        hide_index=True,
    )


def show_developers():
    st.subheader(t("team_title"))
    st.write(t("team_intro"))
    for member in members():
        with st.container(border=True):
            photo, details = st.columns([1, 3], gap="large")
            with photo:
                image = profile_image(member)
                if image:
                    st.image(str(image), width=180)
                else:
                    # Use the member's name when a replaceable photo is absent.
                    name_parts = [
                        part
                        for part in member["name"].replace(".", "").split()
                        if part.casefold() not in {"md", "dr", "bt", "binti", "bin"}
                    ]
                    initials = "".join(part[0] for part in name_parts[:2]).upper() or "SB"
                    st.markdown(
                        f'<div class="sb-initials">{escape(initials)}</div>', unsafe_allow_html=True
                    )
            with details:
                st.markdown(
                    f'<div class="sb-role">{escape(t("team_leader" if member["id"] == "leader" else "team_member"))}</div>',
                    unsafe_allow_html=True,
                )
                st.subheader(member["name"])
                status = (
                    t("pursuing")
                    if member["study_status"] == "Pursuing"
                    else member["study_status"]
                )
                for label, value in [
                    ("degree", f"{member["degree"]} · {status}"),
                    ("faculty", member["faculty"]),
                    ("university", member["university"]),
                    ("email", member["email"]),
                    ("phone", member["phone"]),
                ]:
                    st.write(f"**{t(label)}:** {value}")
                if member["whatsapp_only"]:
                    st.caption(t("whatsapp_only"))
                if member["email"] != "XXXXYYYY":
                    c1, c2 = st.columns(2)
                    c1.link_button(t("email_member"), "mailto:" + member["email"])
                    if member["whatsapp_number"].isdigit():
                        c2.link_button(
                            t("whatsapp_member"), "https://wa.me/" + member["whatsapp_number"]
                        )
                else:
                    st.caption(t("placeholder_member"))


def update_setting(field, widget):
    settings = st.session_state.settings
    settings[field] = st.session_state[widget]
    if field == "fx_mode":
        for key in (
            "comparison",
            "quote",
            "conversion",
            "answer",
            "budget_conversion",
            "personal_forecast",
        ):
            st.session_state.pop(key, None)
    if field == "provider":
        st.session_state.pop("planner_input", None)
        st.session_state.pop("reviewer_input", None)


def update_model(role):
    settings = st.session_state.settings
    settings["models"][settings["provider"]][role] = st.session_state[role + "_input"]


def model_config():
    settings = st.session_state.settings
    provider = settings["provider"]
    models = settings["models"].get(provider, settings["models"]["groq"])
    return ModelConfig(provider, models["planner"], models["reviewer"])


def show_guide():
    st.subheader(t("guide"))
    st.write(t("guide_intro"))
    with st.expander(t("guide_v4_title"), expanded=True):
        st.write(t("guide_v4_body"))
        st.write(t("pilot_login"))
        st.write(t("reset_help"))
        st.write(t("guide_ai_limits"))
        st.write(t("private_data"))
        st.write(t("profile_pdf_note"))
    for title, body in [
        ("guide_start", "guide_start_body"),
        ("guide_fees", "guide_fees_body"),
        ("guide_transfer", "guide_transfer_body"),
        ("guide_pdf", "guide_pdf_body"),
    ]:
        with st.expander(t(title), expanded=title == "guide_start"):
            st.write(t(body))
            if title == "guide_pdf":
                st.info(t("pdf_note"))
    with st.expander(t("guide_questions")):
        st.write(t("guide_question_note"))
        examples = {
            "en": [
                "Convert 12000 BDT to RMB",
                "Convert 2000 CNY to MYR",
                "Compare 100 USD to CNY",
                "Zhejiang Computer Science tuition",
                "Help with my tuition budget",
                "How much is my tuition fee and when should I pay?",
            ],
            "bn": [
                "12000 BDT থেকে RMB হিসাব করো",
                "2000 CNY থেকে MYR হিসাব করো",
                "100 USD থেকে CNY provider তুলনা করো",
                "Zhejiang Computer Science tuition",
                "আমার টিউশন বাজেট করতে সাহায্য করো",
                "আমার সেমিস্টার ফি কত এবং কখন দিতে হবে?",
            ],
            "zh": [
                "将 12000 BDT 转换为 RMB",
                "将 2000 CNY 转换为 MYR",
                "比较 100 USD 到 CNY",
                "Zhejiang Computer Science tuition",
                "帮我制定学费预算",
                "我的学费是多少，什么时候缴费？",
            ],
            "ms": [
                "Tukar 12000 BDT kepada RMB",
                "Tukar 2000 CNY kepada MYR",
                "Banding 100 USD kepada CNY",
                "Zhejiang Computer Science tuition",
                "Bantu saya merancang bajet yuran",
                "Berapakah yuran saya dan bila perlu bayar?",
            ],
        }
        for example in examples[t.language]:
            st.code(example, language=None)
    with st.expander(t("connections")):
        settings = st.session_state.settings
        st.selectbox(
            t("fx_source"),
            ["live", "demo"],
            index=0 if settings["fx_mode"] == "live" else 1,
            format_func=lambda value: t("live" if value == "live" else "offline"),
            key="fx_mode_input",
            on_change=update_setting,
            args=("fx_mode", "fx_mode_input"),
        )
        st.caption(t("fx_settings_help"))
        labels = {"offline": "offline_engine", "groq": "groq_engine", "ollama": "ollama_engine"}
        if os.getenv("STUDENTBRIDGE_DEPLOYMENT") == "cloud":
            labels.pop("ollama")
            if settings["provider"] == "ollama":
                settings["provider"] = "offline"
        provider = st.selectbox(
            t("ai_engine"),
            list(labels),
            index=list(labels).index(settings["provider"]),
            format_func=lambda value: t(labels[value]),
            key="provider_input",
            on_change=update_setting,
            args=("provider", "provider_input"),
        )
        if provider != "offline":
            for role, label in [("planner", "planner_model"), ("reviewer", "reviewer_model")]:
                st.text_input(
                    t(label),
                    settings["models"][provider][role],
                    max_chars=100,
                    placeholder=hint(t, "model"),
                    key=role + "_input",
                    on_change=update_model,
                    args=(role,),
                )
            if st.button(t("model_list"), key="model_list"):
                try:
                    st.write(JSONClient(model_config()).models())
                except Exception:
                    st.error(t("models_unavailable"))
        if provider == "groq":
            st.checkbox(
                t("cloud_consent"),
                value=settings["cloud_consent"],
                key="cloud_consent_input",
                on_change=update_setting,
                args=("cloud_consent", "cloud_consent_input"),
            )
        st.write(t("engine_help"))
    with st.expander(t("security_guide")):
        st.write(t("security_body"))
        st.write(t("private_data"))
        st.write(t("delete_note"))
    with st.expander(t("setup_guide")):
        st.write(t("guide_developer_file"))
        st.caption(t("photo_help"))
        st.code("assets/team/leader/profile.png\nassets/team/member2/profile.png", language=None)
        st.caption(t("source_original_note"))


# Public pages are available before login. They do not expose account data.
if page == "developer":
    show_developers()
    st.stop()
if page == "guide":
    show_guide()
    st.stop()

backend = os.getenv("STUDENTBRIDGE_BACKEND", "local")
try:
    if backend not in {"local", "supabase"}:
        raise FinanceError("STUDENTBRIDGE_BACKEND must be local or supabase.")
    if os.getenv("STUDENTBRIDGE_DEPLOYMENT") == "cloud" and backend != "supabase":
        raise FinanceError("Cloud deployment requires Supabase; local fallback is disabled.")
    if backend == "supabase":
        state = st.session_state.setdefault("_cloud_auth", {})
        store = CloudStore(state)
        risk, catalog = shared_resources()
    else:
        directory = Path(os.getenv("STUDENTBRIDGE_DATA_DIR", "runtime"))
        if not directory.is_absolute():
            directory = ROOT / directory
        store, risk, catalog = resources(str(directory))
    st.sidebar.caption(t("cloud_storage" if backend == "supabase" else "local_storage"))
except Exception as exc:
    st.error(t("setup_missing"))
    if isinstance(exc, FinanceError):
        st.caption(str(exc))
    st.stop()

if not store.has_users():
    st.subheader(t("setup_title"))
    st.write(t("setup_text"))
    with st.form("first_setup"):
        username = st.text_input(
            t("username"),
            value="student",
            max_chars=32,
            key="setup_username",
            placeholder=hint(t, "username"),
        )
        password = st.text_input(
            t("choose_password"),
            type="password",
            max_chars=128,
            key="setup_password",
            placeholder=hint(t, "new_password"),
        )
        again = st.text_input(
            t("repeat_password"),
            type="password",
            max_chars=128,
            key="setup_repeat",
            placeholder=hint(t, "repeat_password"),
        )
        submitted = st.form_submit_button(t("create_account"))
    if submitted:
        try:
            if password != again:
                st.error(t("password_mismatch"))
            else:
                store.create_user(username, password, first_only=True)
                accept_login(store.login(username, password))
                st.rerun()
        except FinanceError as exc:
            display_error(exc)
    st.caption(t("account_help"))
    st.stop()

token = st.session_state.get("token")
try:
    user = store.principal(token)
except FinanceError:
    st.session_state.pop("token", None)
    st.subheader(t("login_title"))
    st.write(t("pilot_login") if backend == "supabase" else t("login_sub"))
    with st.form("login"):
        username = st.text_input(
            t("email_login" if backend == "supabase" else "username"),
            max_chars=254 if backend == "supabase" else 32,
            key="login_username",
            placeholder=hint(t, "email" if backend == "supabase" else "username"),
        )
        password = st.text_input(
            t("password"),
            type="password",
            max_chars=128,
            key="login_password",
            placeholder=hint(t, "password"),
        )
        submitted = st.form_submit_button(t("sign_in"))
    if submitted:
        token = store.login(username, password)
        if token:
            accept_login(token)
            st.rerun()
        else:
            st.error(
                t("login_title") + ": " + t("reset_help")
                if backend == "supabase"
                else t("login_failed")
            )
    st.caption(t("account_help"))
    st.stop()

with st.sidebar:
    role_key = "planner_role" if user["role"] == "planner" else user["role"]
    st.divider()
    st.caption(t("signed_in", name=user["username"], role=t(role_key)))
    st.caption(t("session_note"))
    if st.button(t("sign_out"), key="sign_out"):
        try:
            store.logout(token)
        except FinanceError:
            pass  # Local tokens are cleared even during a provider outage.
        clear_session()
        st.rerun()

settings = st.session_state.settings
mode = settings["fx_mode"]
fx = FXService(mode)
broker = CloudBroker(store, fx, risk) if backend == "supabase" else SandboxBroker(store, fx, risk)
config = model_config()
cloud_consent = settings["cloud_consent"]

if page == "account":
    account_page(t, store, token, clear_session)
    st.stop()
if page == "forecast":
    try:
        forecast_page(t, store, token, fx, catalog, config, cloud_consent)
    except FinanceError as exc:
        display_error(exc)
    st.stop()

if page == "dashboard":
    st.subheader(t("overview_title"))
    st.write(t("overview_sub"))
    try:
        personal = store.student_profile(token)
        if personal:
            st.write(f"**{personal["university"]} · {personal["programme"]}**")
            st.caption(t("profile_updated", date=personal.get("updated_at", "")))
        else:
            st.info(t("profile_required"))
        st.button(t("profile_assistant"), on_click=go, args=("forecast",), key="dashboard_profile")
    except FinanceError as exc:
        display_error(exc)
    try:
        balances = store.wallet(token)
    except FinanceError as exc:
        display_error(exc)
        balances = {}
    bundle = st.session_state.get("budget")
    cols = st.columns(4)
    cols[0].metric(t("planner_metric"), 10)
    cols[1].metric(t("programme_metric"), len(catalog.records))
    cols[2].metric(t("balance_metric"), len(balances))
    cols[3].metric(t("reference_metric"), t("live") if mode == "live" else t("offline"))
    st.subheader(t("last_budget"))
    if bundle:
        result = bundle["result"]
        c1, c2, c3 = st.columns(3)
        c1.metric(t("estimated_cost"), f"{result["total"]} {result["currency"]}")
        c2.metric(t("resources"), f"{result["resources"]} {result["currency"]}")
        c3.metric(t("gap"), f"{result["funding_gap"]} {result["currency"]}")
    else:
        st.info(t("no_budget"))
    st.subheader(t("quick_actions"))
    c1, c2, c3 = st.columns(3)
    c1.button(t("open_planner"), on_click=go, args=("planner",), width="stretch")
    c2.button(t("open_converter"), on_click=go, args=("converter",), width="stretch")
    c3.button(t("open_transfers"), on_click=go, args=("transfers",), width="stretch")
    st.subheader(t("recent_activity"))
    try:
        audit = store.export_audit(token)
    except FinanceError as exc:
        display_error(exc)
        audit = {"own_events": []}
    completed = [
        event for event in audit["own_events"] if event["event"] == "sandbox_transfer_completed"
    ]
    if completed:
        st.dataframe(
            [
                {
                    t("receipt_id"): e["details"]["quote_id"],
                    t("spend"): f"{e["details"]["spent"]} {e["details"]["source"]}",
                    t("received"): f"{e["details"]["received"]} {e["details"]["target"]}",
                }
                for e in reversed(completed[-5:])
            ],
            hide_index=True,
        )
    else:
        st.caption(t("no_activity"))
    st.stop()

# Only pages needing a currency catalogue access the rate service. Developer,
# Guide, Dashboard and sign-in remain available during a provider outage.
try:
    with st.spinner(t("loading_currencies")):
        codes = currency_catalog(mode)
except FinanceError:
    st.error(t("fx_unavailable"))
    if st.button(t("retry"), key="retry_catalogue"):
        currency_catalog.clear()
        st.rerun()
    st.button(t("open_guide"), on_click=go, args=("guide",))
    st.stop()

if page == "profile":
    try:
        profile_page(t, store, token, catalog, codes)
    except FinanceError as exc:
        display_error(exc)
elif page == "assistant":
    st.subheader(t("ask_title"))
    st.button(t("profile_assistant"), on_click=go, args=("forecast",), key="assistant_profile")
    with st.container(border=True):
        question = st.text_area(
            t("question"), placeholder=t("question_placeholder"), max_chars=1200, key="question"
        )
        submitted = st.button(t("run_assistant"), key="action_run_assistant")
    if submitted:
        if not question.strip():
            st.warning(t("question_required"))
        else:
            try:
                st.session_state.pop("answer", None)
                personal = personal_fee_answer(question, lambda: store.student_profile(token))
                if personal is not None:
                    st.session_state.answer = personal
                else:
                    if config.provider != "offline":
                        if config.provider == "groq" and not cloud_consent:
                            raise FinanceError(
                                "Enable cloud consent in Guide for User before requesting AI review."
                            )
                        store.reserve_ai(token)
                    with st.spinner(t("processing")):
                        st.session_state.answer = FinanceAgent(
                            fx, catalog, config, comparator=broker.compare
                        ).answer(question, cloud_consent=cloud_consent, dual=True)
            except FinanceError as exc:
                display_error(exc)
    answer = st.session_state.get("answer")
    if answer:
        if answer["status"] == "error":
            display_error(FinanceError(answer.get("message", "")))
        elif answer["status"] != "ok":
            st.warning(t("blocked") if answer["status"] == "blocked" else t("clarify"))
            with st.expander(t("technical_details")):
                st.write(answer.get("message", ""))
        elif answer["kind"] == "personal_fee":
            render_personal_fee(st, t.language, answer)
        elif answer["kind"] == "conversion":
            result = answer["facts"]
            st.metric(t("converted"), f"{result["converted"]} {result["target"]}")
            st.write(
                f"{result["amount"]} {result["base"]} → {result["converted"]} {result["target"]}"
            )
            reference(result["reference"])
            pdf_download(
                "pdf_statement",
                conversion_statement(result),
                "StudentBridge_Conversion.pdf",
                "answer_pdf",
            )
        elif answer["kind"] == "university":
            programme_card(answer["facts"])
            pdf_download(
                "pdf_summary",
                university_statement(answer["facts"]),
                "StudentBridge_University_Reference.pdf",
                "answer_pdf",
            )
        elif answer["kind"] == "comparison":
            provider_table(answer["facts"])
            reference(answer["facts"][0]["reference"])
            pdf_download(
                "pdf_statement",
                comparison_statement(answer["facts"]),
                "StudentBridge_Transfer_Options.pdf",
                "answer_pdf",
            )
        else:
            st.info(t("use_planner"))

elif page == "converter":
    st.subheader(t("converter"))
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            source = select_currency("from", codes, "BDT", "convert_source")
        with c2:
            target = select_currency("to", codes, "CNY", "convert_target")
        amount = st.text_input(
            t("source_amount"),
            value="",
            max_chars=32,
            key="convert_amount",
            placeholder=hint(t, "amount"),
        )
        reverse = st.checkbox(t("reverse"), key="reverse_conversion")
        submitted = st.button(t("calculate_conversion"), key="action_calculate_conversion")
    if submitted:
        try:
            if reverse:
                source, target = target, source
            st.session_state.conversion = fx.convert(amount, source, target)
        except FinanceError as exc:
            display_error(exc)
    result = st.session_state.get("conversion")
    if result:
        st.metric(t("converted"), f"{result["converted"]} {result["target"]}")
        st.write(f"{result["amount"]} {result["base"]} → {result["converted"]} {result["target"]}")
        reference(result["reference"])
        st.subheader(t("sensitivity"))
        rows = []
        for change in ("-0.10", "-0.05", "0", "0.05", "0.10"):
            rate = Decimal(result["reference"]["rate"]) * (1 + Decimal(change))
            rows.append(
                {
                    t("movement"): f"{Decimal(change) * 100:+.0f}%",
                    t(
                        "received"
                    ): f"{rounded(Decimal(result["amount"]) * rate, result["target"])} {result["target"]}",
                }
            )
        st.dataframe(rows, hide_index=True)
        st.caption(t("sensitivity_note"))
        pdf_download(
            "pdf_statement",
            conversion_statement(result),
            "StudentBridge_Conversion.pdf",
            "conversion_pdf",
        )

elif page == "planner":
    st.subheader(t("planner"))
    c1, c2 = st.columns(2)
    country = c1.selectbox(
        t("country"),
        ["all", "Malaysia", "Bangladesh", "China"],
        format_func=t,
        key="country_filter",
    )
    level = c2.selectbox(
        t("level"), ["all", "Bachelor", "Master"], format_func=t, key="level_filter"
    )
    available = [
        r
        for r in catalog.records
        if (country == "all" or r["country"] == country) and (level == "all" or r["level"] == level)
    ]
    if not available:
        st.info(t("no_programme"))
        st.stop()
    record_id = st.selectbox(
        t("programme"),
        [r["id"] for r in available],
        key="programme_id",
        format_func=lambda i: (
            f"{catalog.get(i)["abbr"]} · {catalog.get(i)["programme"]} · {t(catalog.get(i)["student_type"])}"
        ),
    )
    record = catalog.get(record_id)
    with st.expander(t("official_reference"), expanded=True):
        programme_card(record)
    st.caption(t("living_note"))
    saved = store.profile(token)
    loaded = saved if saved.get("record_id") == record_id else {}
    use_saved = st.checkbox(
        t("load_saved"), value=False, disabled=not bool(loaded), key="load_saved"
    )
    defaults = loaded if use_saved else {}
    # Per-programme keys preserve entered financial values across language changes.
    prefix = record_id + ("_saved" if use_saved else "_new")

    def text_input(key, default, max_chars=32):
        return st.text_input(
            t(key),
            defaults.get(key, default),
            max_chars=max_chars,
            key=prefix + key,
            placeholder=hint(t, "amount"),
        )

    with st.container(border=True):
        st.write(t("inputs_currency", currency=record["currency"]))
        col1, col2, col3 = st.columns(3)
        with col1:
            tuition = st.text_input(
                t("tuition_fee"),
                defaults.get("tuition", record["fee"] or "0"),
                max_chars=32,
                key=prefix + "tuition",
                placeholder=hint(t, "amount"),
            )
            periods = ["programme", "year", "semester", "trimester", "invoice"]
            period_default = defaults.get("fee_period", record["fee_period"])
            fee_period = st.selectbox(
                t("fee_period"),
                periods,
                index=periods.index(period_default) if period_default in periods else 4,
                format_func=lambda p: t("programme_period" if p == "programme" else p),
                key=prefix + "fee_period",
            )
            months = st.number_input(
                t("months"),
                min_value=1,
                max_value=96,
                value=int(defaults.get("months", record["planning_months"])),
                key=prefix + "months",
            )
            count_default = math.ceil(months / 12) if fee_period == "year" else 1
            tuition_periods = st.number_input(
                t("fee_count"),
                min_value=1,
                max_value=24,
                value=int(defaults.get("tuition_periods", count_default)),
                help=t("fee_count_help"),
                key=prefix + "count",
            )
        with col2:
            living = {
                field: st.text_input(
                    t(field),
                    defaults.get("living", {}).get(field, record["living_monthly"][field]),
                    max_chars=32,
                    key=prefix + field,
                    placeholder=hint(t, "amount"),
                )
                for field in ("rent", "food", "transport", "utilities", "other")
            }
            one_off = text_input("one_off", "0")
        with col3:
            tax_percent = st.text_input(
                t("tax"),
                defaults.get("tax_percent", "6" if record_id in {"um_meng_int", "iium_mmgt"} else "0"),
                max_chars=8,
                key=prefix + "tax",
                placeholder=hint(t, "percent"),
            )
            buffer_percent = st.text_input(
                t("contingency"),
                defaults.get("buffer_percent", "10"),
                max_chars=8,
                key=prefix + "contingency",
                placeholder=hint(t, "percent"),
            )
            savings = text_input("savings", "0")
            monthly_income = st.text_input(
                t("income"),
                defaults.get("monthly_income", "0"),
                max_chars=32,
                key=prefix + "income",
                placeholder=hint(t, "amount"),
            )
            confirmed_funding = st.text_input(
                t("funding"),
                defaults.get("confirmed_funding", "0"),
                max_chars=32,
                key=prefix + "funding",
                placeholder=hint(t, "amount"),
            )
        confirmed = st.checkbox(t("confirm_fee"), key=prefix + "confirmed")
        save = st.checkbox(t("save_plan"), key=prefix + "save")
        submitted = st.button(t("calculate_budget"), key="action_calculate_budget")
    if submitted:
        try:
            if not confirmed:
                st.error(t("confirm_required"))
            elif record["status"] == "manual_required" and decimal(tuition) <= 0:
                st.error(t("manual_fee"))
            else:
                inputs = dict(
                    code=record["currency"],
                    tuition=tuition,
                    fee_period=fee_period,
                    tuition_periods=int(tuition_periods),
                    months=int(months),
                    living=living,
                    one_off=one_off,
                    tax_percent=tax_percent,
                    buffer_percent=buffer_percent,
                    savings=savings,
                    monthly_income=monthly_income,
                    confirmed_funding=confirmed_funding,
                )
                result = budget_scenario(**inputs)
                st.session_state.budget = {
                    "record_id": record_id,
                    "inputs": inputs,
                    "result": result,
                    "source_url": record["source_url"],
                    "reference_status": record["status"],
                    "created_at": time.time(),
                }
                if save:
                    store.save_profile(token, {"record_id": record_id, **inputs})
        except (FinanceError, ValueError) as exc:
            display_error(exc)
    bundle = st.session_state.get("budget")
    if bundle and bundle["record_id"] == record_id:
        result = bundle["result"]
        cols = st.columns(3)
        for col, label, field in zip(
            cols, ["estimated_cost", "resources", "gap"], ["total", "resources", "funding_gap"]
        ):
            col.metric(t(label), f"{result[field]} {result["currency"]}")
        fields = ["tuition", "tax_assumption", "living_total", "one_off", "contingency"]
        labels = ["tuition", "tax_amount", "living", "one_off", "buffer"]
        amounts = [result[field] for field in fields]
        chart = pd.DataFrame(
            {
                t("category"): [t(label) for label in labels],
                t("amount"): [float(value) for value in amounts],
            }
        )
        st.bar_chart(chart.set_index(t("category")), color="#a12d3a")
        st.dataframe(
            {
                t("category"): [t(label) for label in labels],
                t("amount"): [f"{value} {result["currency"]}" for value in amounts],
            },
            hide_index=True,
        )
        st.subheader(t("budget_actions"))
        st.write("• " + t("verify_fee_advice"))
        st.write("• " + t("housing_advice", city=record["city"]))
        if Decimal(result["funding_gap"]) > 0:
            st.write(
                "• "
                + t(
                    "gap_advice",
                    amount=result["funding_gap"],
                    currency=result["currency"],
                    months=result["months"],
                    monthly=result["extra_monthly_saving"],
                )
            )
        else:
            st.write("• " + t("covered_advice"))
        st.write("• " + t("funding_advice"))
        if config.provider != "offline" and st.button(t("prioritize"), key="prioritize"):
            try:
                if config.provider == "groq" and not cloud_consent:
                    raise FinanceError(
                        "Enable cloud consent in Guide for User before requesting AI review."
                    )
                store.reserve_ai(token)
                with st.spinner(t("advice_processing")):
                    advice = FinanceAgent(fx, catalog, config).budget_advice(
                        result, record, cloud_consent=cloud_consent
                    )
                # Keep monetary wording deterministic in the selected UI language.
                for action in advice.get("agreed_actions", []):
                    mapping = {
                        "VERIFY_FEE": "verify_fee_advice",
                        "COMPARE_HOUSING": "housing_advice",
                        "SAVE_FOR_GAP": "gap_advice",
                        "CONFIRM_FUNDING": "funding_advice",
                        "CHECK_DUE_DATE": "due_title",
                        "FX_BUFFER": "sensitivity",
                    }
                    st.write(
                        "• "
                        + t(
                            mapping[action],
                            city=record["city"],
                            amount=result["funding_gap"],
                            currency=result["currency"],
                            months=result["months"],
                            monthly=result["extra_monthly_saving"],
                        )
                    )
                st.caption(t("model_agreed"))
            except FinanceError as exc:
                display_error(exc)
        home = select_currency("home_currency", codes, "BDT", "budget_home")
        if st.button(t("convert_total"), key="convert_budget"):
            try:
                converted = fx.convert(result["total"], result["currency"], home)
                st.success(f"{converted["converted"]} {home}")
                reference(converted["reference"])
            except FinanceError as exc:
                display_error(exc)
        pdf_download(
            "pdf_invoice",
            planning_invoice(bundle, record),
            "StudentBridge_Planning_Invoice.pdf",
            "invoice_pdf",
        )
    st.divider()
    st.subheader(t("due_title"))
    with st.container(border=True):
        due_amount = st.text_input(
            t("due_amount"),
            value="",
            max_chars=32,
            key="due_amount",
            placeholder=hint(t, "amount"),
        )
        available_cash = st.text_input(
            t("due_available"),
            "0",
            max_chars=32,
            key="due_available",
            placeholder=hint(t, "amount"),
        )
        due_months = st.number_input(
            t("due_months"), min_value=1, max_value=60, value=3, key="due_months"
        )
        submitted = st.button(t("due_calculate"), key="action_due_calculate")
    if submitted:
        try:
            due = due_plan(due_amount, available_cash, int(due_months), record["currency"])
            st.success(
                t(
                    "due_result",
                    amount=due["save_per_month"],
                    currency=due["currency"],
                    months=due["months"],
                )
            )
        except FinanceError as exc:
            display_error(exc)

elif page == "transfers":
    st.subheader(t("transfer_title"))
    st.caption(t("transfer_note"))
    with st.container(border=True):
        source = select_currency("spend_currency", codes, "BDT", "transfer_source")
        target = select_currency("receive_currency", codes, "CNY", "transfer_target")
        amount = st.text_input(
            t("spend_budget"),
            value="",
            max_chars=32,
            key="transfer_amount",
            placeholder=hint(t, "amount"),
        )
        new_recipient = st.checkbox(t("new_recipient"), key="new_recipient")
        submitted = st.button(t("compare"), key="action_compare")
    if submitted:
        try:
            options = broker.compare(amount, source, target)
            st.session_state.comparison = {
                "options": options,
                "amount": amount,
                "source": source,
                "target": target,
                "new_recipient": new_recipient,
                "mode": mode,
            }
            st.session_state.pop("quote", None)
        except FinanceError as exc:
            display_error(exc)
    comparison = st.session_state.get("comparison")
    if comparison:
        options = comparison["options"]
        provider_table(options)
        reference(options[0]["reference"])
        provider_name = st.selectbox(
            t("select_provider"), [r["provider"] for r in options], key="quote_provider"
        )
        if st.button(t("create_quote"), disabled=user["role"] == "viewer", key="create_quote"):
            try:
                if comparison["mode"] != mode:
                    st.error(t("mode_changed"))
                else:
                    st.session_state.quote = broker.create_quote(
                        token,
                        comparison["amount"],
                        comparison["source"],
                        comparison["target"],
                        provider_name,
                        new_recipient=comparison["new_recipient"],
                    )
            except FinanceError as exc:
                display_error(exc)
    quote = st.session_state.get("quote")
    if quote:
        st.subheader(t("review_quote"))
        st.write(
            t(
                "quote_summary",
                spend=major(quote["spend_minor"], quote["source"]),
                source=quote["source"],
                fee=major(quote["fee_minor"], quote["source"]),
                received=major(quote["receive_minor"], quote["target"]),
                target=quote["target"],
                provider=quote["provider"],
            )
        )
        reference(quote["reference"])
        st.caption(
            t("quote_expiry", id=quote["id"], seconds=max(0, int(quote["expires"] - time.time())))
        )
        (st.error if quote["risk"]["blocked"] else st.success)(
            t("risk_blocked" if quote["risk"]["blocked"] else "risk_passed")
        )
        with st.form("execute_" + quote["id"]):
            approved = st.checkbox(t("approve"), key="approve_" + quote["id"])
            confirmation = st.text_input(
                t("confirmation", code=quote["id"][-6:]),
                max_chars=6,
                key="confirm_" + quote["id"],
                placeholder=hint(t, "confirmation"),
            )
            execute = st.form_submit_button(
                t("execute"), disabled=user["role"] != "executor" or quote["risk"]["blocked"]
            )
        if execute:
            try:
                receipt = broker.execute(token, quote["id"], confirmation, approved=approved)
                st.session_state.receipt = receipt
                st.success(t("transfer_completed"))
                if receipt["replayed"]:
                    st.info(t("replay"))
            except FinanceError as exc:
                display_error(exc)
    receipt = st.session_state.get("receipt")
    if receipt:
        st.subheader(t("receipt_details"))
        st.dataframe(
            [
                {t("category"): t(label), t("amount"): value}
                for label, value in [
                    ("receipt_id", receipt["quote_id"]),
                    ("spend", f"{receipt["spent"]} {receipt["source"]}"),
                    ("fee_included", f"{receipt["fee_included"]} {receipt["source"]}"),
                    ("received", f"{receipt["received"]} {receipt["target"]}"),
                ]
            ],
            hide_index=True,
        )
        pdf_download(
            "pdf_receipt", transfer_receipt(receipt), "StudentBridge_Receipt.pdf", "receipt_pdf"
        )

elif page == "wallet":
    st.subheader(t("wallet_title"))
    try:
        balances = store.wallet(token)
    except FinanceError as exc:
        display_error(exc)
        st.stop()
    if balances:
        st.dataframe(
            [
                {t("currency"): code, t("balance"): major(value, code)}
                for code, value in sorted(balances.items())
            ],
            hide_index=True,
        )
    else:
        st.info(t("wallet_empty"))
    st.subheader(t("add_funds_title"))
    with st.container(border=True):
        code = select_currency("fund_currency", codes, "BDT", "wallet_currency")
        amount = st.text_input(
            t("fund_amount"),
            value="",
            max_chars=32,
            key="wallet_amount",
            placeholder=hint(t, "amount"),
        )
        add = st.button(t("add_funds"), key="action_add_funds", disabled=user["role"] != "executor")
    if add:
        try:
            store.seed_wallet(token, code, amount)
            st.rerun()
        except FinanceError as exc:
            display_error(exc)
    st.caption(t("wallet_note"))
    st.subheader(t("audit_title"))
    try:
        audit = store.export_audit(token)
        integrity = audit["global_integrity"]
    except FinanceError as exc:
        display_error(exc)
        st.stop()
    if integrity["valid"]:
        st.success(t("audit_verified", count=integrity["rows"]))
    else:
        st.error(t("audit_failed"))
    with st.expander(t("audit_history")):
        try:
            st.dataframe(
                [
                    {
                        t("seq"): e["seq"],
                        t("event"): t("login_event" if e["event"] == "login" else e["event"]),
                        t("time"): datetime.fromtimestamp(e["stamp"], timezone.utc).strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                    }
                    for e in audit["own_events"]
                ],
                hide_index=True,
            )
            pdf_download(
                "pdf_statement",
                audit_statement(audit),
                "StudentBridge_Activity_Statement.pdf",
                "audit_pdf",
            )
        except FinanceError as exc:
            display_error(exc)
