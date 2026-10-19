"""Profile workflow kept outside app.py so account state is explicit in every call."""

from datetime import date
import pandas as pd
import streamlit as st

from .agent import FinanceAgent
from .cloud import CloudStore
from .documents import student_profile_pdf, forecast_pdf
from .money import FinanceError
from .profile import validated_profile, forecast
from .ui_hints import hint


def profile_page(t, store, token, catalog, codes):
    st.subheader(t("profile"))
    st.write(t("profile_intro"))
    saved = store.student_profile(token)
    if saved:
        st.caption(t("profile_updated", date=saved.get("updated_at", "")))
    # The catalogue supplies names and references. It never overwrites user fees.
    with st.expander(t("official_reference")):
        for abbr in sorted({r["abbr"] for r in catalog.records}):
            record = next(r for r in catalog.records if r["abbr"] == abbr)
            st.write(f"**{abbr}** · {record["university"]} · {record["city"]}")
            st.link_button(t("source_link") + " · " + abbr, record["source_url"])

    def select_code(label, default, key):
        available = sorted(set(codes) | {default})
        return st.selectbox(
            t(label),
            available,
            index=available.index(default),
            format_func=t.currency_label,
            key=key,
        )

    def money_input(label, value, key):
        example = "percent" if label in {"contingency", "cost_growth", "fx_stress"} else "amount"
        return st.text_input(
            t(label),
            str(value),
            max_chars=32,
            key=key,
            placeholder=hint(t, example),
        )

    def amt(field, default="0"):
        return saved.get(field, {}).get("amount", default)

    with st.form("student_profile_form"):
        left, right = st.columns(2)
        with left:
            university = st.text_input(
                t("university"),
                saved.get("university", ""),
                max_chars=140,
                key="p_university",
                placeholder=hint(t, "university"),
            )
            campus = st.text_input(
                t("campus"),
                saved.get("campus", ""),
                max_chars=100,
                key="p_campus",
                placeholder=hint(t, "campus"),
            )
            department = st.text_input(
                t("department"),
                saved.get("department", ""),
                max_chars=140,
                key="p_department",
                placeholder=hint(t, "department"),
            )
            programme = st.text_input(
                t("programme"),
                saved.get("programme", ""),
                max_chars=140,
                key="p_programme",
                placeholder=hint(t, "programme"),
            )
            study_mode = st.text_input(
                t("study_mode"),
                saved.get("study_mode", "Research"),
                max_chars=50,
                key="p_study_mode",
                placeholder=hint(t, "study_mode"),
            )
            city = st.text_input(
                t("city_input"),
                saved.get("city", ""),
                max_chars=100,
                key="p_city",
                placeholder=hint(t, "city"),
            )
            country = st.text_input(
                t("country"),
                saved.get("country", ""),
                max_chars=80,
                key="p_country",
                placeholder=hint(t, "country"),
            )
            start = st.date_input(
                t("start_date"),
                date.fromisoformat(saved["start_date"]) if saved else date.today(),
                key="p_start",
            )
            months = st.number_input(
                t("months"),
                min_value=1,
                max_value=96,
                value=saved.get("months", 12),
                key="p_months",
            )
            base = select_code("budget_currency", saved.get("budget_currency", "MYR"), "p_base")
            tuition_code = select_code(
                "tuition_currency",
                saved.get("tuition", {}).get("currency", "MYR"),
                "p_tuition_code",
            )
            tuition = money_input("tuition_fee", amt("tuition"), "p_tuition")
            periods = ["semester", "year", "trimester", "programme", "invoice"]
            period = st.selectbox(
                t("fee_period"),
                periods,
                index=periods.index(saved.get("fee_period", "semester")),
                format_func=lambda x: t("programme_period" if x == "programme" else x),
                key="p_fee_period",
            )
            interval = st.number_input(
                t("billing_interval"),
                min_value=0,
                max_value=24,
                value=saved.get("billing_interval_months", 6),
                help=t("billing_help"),
                key="p_interval",
            )
            due = st.date_input(
                t("next_tuition"),
                date.fromisoformat(saved["next_tuition_date"]) if saved else date.today(),
                key="p_due",
            )
        with right:
            living_code = select_code(
                "living_currency",
                saved.get("living", {}).get("rent", {}).get("currency", "MYR"),
                "p_living_code",
            )
            living = {
                k: money_input(k, saved.get("living", {}).get(k, {}).get("amount", "0"), "p_" + k)
                for k in ["rent", "food", "transport", "utilities", "other"]
            }
            oneoff_code = select_code(
                "oneoff_currency", saved.get("one_off", {}).get("currency", "MYR"), "p_oneoff_code"
            )
            oneoff = money_input("one_off", amt("one_off"), "p_oneoff")
            resources_code = select_code(
                "resources_currency",
                saved.get("savings", {}).get("currency", "MYR"),
                "p_resources_code",
            )
            savings = money_input("savings", amt("savings"), "p_savings")
            income = money_input("income", amt("monthly_income"), "p_income")
            funding = money_input("funding", amt("confirmed_funding"), "p_funding")
            buffer = money_input("contingency", saved.get("buffer_percent", "10"), "p_buffer")
            growth = money_input(
                "cost_growth", saved.get("annual_cost_growth_percent", "0"), "p_growth"
            )
            stress = money_input("fx_stress", saved.get("fx_stress_percent", "0"), "p_stress")
            st.caption(t("stress_help"))
            note = st.text_area(
                t("source_note"), saved.get("source_note", ""), max_chars=500, key="p_note", placeholder=hint(t, "note")
            )
        confirmed = st.checkbox(t("confirm_profile"), key="p_confirmed")
        submit = st.form_submit_button(t("profile_save"))
    if submit:
        if not confirmed:
            st.error(t("confirm_required"))
        else:

            def item(value, code):
                return {"amount": value, "currency": code}

            value = dict(
                university=university.strip(),
                campus=campus.strip(),
                department=department.strip(),
                programme=programme.strip(),
                study_mode=study_mode.strip(),
                city=city.strip(),
                country=country.strip(),
                start_date=start.isoformat(),
                months=int(months),
                budget_currency=base,
                tuition=item(tuition, tuition_code),
                fee_period=period,
                billing_interval_months=0 if period in {"programme", "invoice"} else int(interval),
                next_tuition_date=due.isoformat(),
                living={k: item(v, living_code) for k, v in living.items()},
                one_off=item(oneoff, oneoff_code),
                savings=item(savings, resources_code),
                monthly_income=item(income, resources_code),
                confirmed_funding=item(funding, resources_code),
                buffer_percent=buffer,
                annual_cost_growth_percent=growth,
                fx_stress_percent=stress,
                source_note=note,
                confirmed=True,
            )
            try:
                value = validated_profile(value)
                store.save_student_profile(token, value)
                st.session_state.pop("personal_forecast", None)
                saved = value
                st.success(t("profile_saved"))
            except FinanceError as exc:
                st.error(str(exc))
    if saved:
        st.caption(t("profile_pdf_note"))
        st.download_button(
            t("profile_pdf"),
            student_profile_pdf(saved),
            file_name="StudentBridge_Profile.pdf",
            mime="application/pdf",
        )


def forecast_page(t, store, token, fx, catalog, config, consent):
    st.subheader(t("forecast"))
    st.write(t("forecast_intro"))
    p = store.student_profile(token)
    if not p:
        st.info(t("profile_required"))
        return
    st.caption(t("profile_updated", date=p.get("updated_at", "")))
    if st.button(t("forecast_run"), key="forecast_run"):
        try:
            st.session_state.personal_forecast = {
                "profile": p,
                "result": forecast(p, fx),
                "mode": fx.mode,
            }
        except (FinanceError, ValueError) as exc:
            st.error(str(exc))
    bundle = st.session_state.get("personal_forecast")
    if not bundle or bundle["profile"] != p or bundle["mode"] != fx.mode:
        return
    r = bundle["result"]
    a, b, c, d = st.columns(4)
    for col, key, field in [
        (a, "estimated_cost", "total"),
        (b, "resources", "resources"),
        (c, "gap", "funding_gap"),
        (d, "timing_gap", "upfront_timing_gap"),
    ]:
        col.metric(t(key), f"{r[field]} {r["currency"]}")
    if r["first_shortfall"]:
        st.warning(t("first_shortfall") + ": " + r["first_shortfall"])
    st.subheader(t("monthly_cashflow"))
    labels = {
        "month": "month_start",
        "tuition_due_dates": "due_dates",
        "living": "living",
        "tuition": "tuition",
        "one_off": "one_off",
        "buffer": "buffer",
        "cost": "total_cost",
        "income": "income",
        "closing_balance": "closing_balance",
    }
    st.dataframe([{t(labels[k]): v for k, v in row.items()} for row in r["rows"]], hide_index=True)
    chart = pd.DataFrame(
        {
            t("month_start"): [x["month"] for x in r["rows"]],
            t("closing_balance"): [float(x["closing_balance"]) for x in r["rows"]],
        }
    )
    st.line_chart(chart.set_index(t("month_start")), color="#a12d3a")
    if r["references"]:
        for ref in r["references"]:
            st.caption(
                f"{ref["base"]} → {ref["quote"]} · {ref["source"]} · {t("reference_date")}: {ref["as_of"]} · {ref["fetched_at"]}"
            )
    else:
        st.caption(t("same_currency_note"))
    st.caption(t("stress_help"))
    with st.expander(t("technical_details")):
        for assumption in r["assumptions"]:
            st.write(assumption)
    st.download_button(
        t("forecast_pdf"),
        forecast_pdf(p, r),
        file_name="StudentBridge_Forecast.pdf",
        mime="application/pdf",
        key="forecast_pdf",
    )
    st.caption(t("profile_ai_note"))
    if config.provider != "offline" and st.button(t("profile_ai"), key="profile_ai"):
        try:
            if config.provider == "groq" and not consent:
                raise FinanceError(
                    "Enable cloud consent in Guide for User before requesting AI review."
                )
            store.reserve_ai(token)
            generic = dict(
                university="User-selected institution",
                programme="user-entered programme",
                city="your study location",
                country="Not shared",
                fee_period=p["fee_period"],
                status="user_provided",
                notes="Numeric scenario only; no personal identifiers.",
            )
            # Monthly rows and source dates are unnecessary for choosing action priorities.
            totals = {
                k: r[k]
                for k in [
                    "currency",
                    "months",
                    "total",
                    "resources",
                    "funding_gap",
                    "extra_monthly_saving",
                    "monthly_living",
                ]
            }
            advice = FinanceAgent(fx, catalog, config).budget_advice(
                totals, generic, cloud_consent=consent
            )
            mapping = {
                "VERIFY_FEE": "verify_fee_advice",
                "COMPARE_HOUSING": "housing_advice",
                "SAVE_FOR_GAP": "gap_advice",
                "CONFIRM_FUNDING": "funding_advice",
                "CHECK_DUE_DATE": "due_title",
                "FX_BUFFER": "sensitivity",
            }
            for action in advice.get("agreed_actions", []):
                st.write(
                    "• "
                    + t(
                        mapping[action],
                        city=p["city"],
                        amount=r["funding_gap"],
                        currency=r["currency"],
                        months=r["months"],
                        monthly=r["extra_monthly_saving"],
                    )
                )
        except FinanceError as exc:
            st.error(str(exc))


def account_page(t, store, token, clear_results):
    st.subheader(t("account"))
    st.write(t("private_data"))
    st.info(t("reset_help") if isinstance(store, CloudStore) else t("account_help"))
    if isinstance(store, CloudStore):
        with st.form("change_password"):
            current = st.text_input(
                t("current_password"),
                type="password",
                max_chars=128,
                placeholder=hint(t, "password"),
            )
            new = st.text_input(
                t("choose_password"),
                type="password",
                max_chars=128,
                placeholder=hint(t, "new_password"),
            )
            again = st.text_input(
                t("repeat_password"),
                type="password",
                max_chars=128,
                placeholder=hint(t, "repeat_password"),
            )
            submit = st.form_submit_button(t("change_password"))
        if submit:
            try:
                if new != again:
                    raise FinanceError(t("password_mismatch"))
                store.change_password(token, current, new)
                store.logout(token)
                clear_results()
                st.success(t("password_changed"))
                st.stop()
            except FinanceError as exc:
                st.error(str(exc))
    st.divider()
    st.write(t("delete_note"))
    confirm = st.checkbox(t("delete_confirm"), key="delete_profiles_confirm")
    if st.button(t("delete_profiles"), disabled=not confirm, key="delete_profiles"):
        try:
            store.clear_personal_data(token)
            for key in ("personal_forecast", "budget", "budget_conversion"):
                st.session_state.pop(key, None)
            st.success(t("deleted_profiles"))
        except FinanceError as exc:
            st.error(str(exc))
