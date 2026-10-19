"""Answer narrow personal tuition questions from the signed-in user's profile.

This path is a local lookup, not an LLM response or an official fee verification.
The caller supplies an authenticated profile loader; questions cannot select a
different account. Profile data and due dates are never sent to Groq here.
"""

import re

from .agent import suspicious_request
from .llm import safe_text
from .money import FinanceError, major, minor
from .profile import StudentProfile


def personal_fee_answer(question, profile_loader):
    """Return a saved-profile answer, or None for the existing general agent."""
    text = safe_text(question)
    if suspicious_request(text):
        return {
            "status": "blocked", "mode": "profile", "calls": [],
            "message": "The question requests a security override. No profile was read.",
        }
    personal = re.search(r"(?i)\b(my|me|i|saya|aku)\b|আমার|আমি|我的|我", text)
    tuition = re.search(r"(?i)\b(tuition|fees?|semester|yuran)\b|টিউশন|সেমিস্টার|ফি|学费|學費", text)
    broader = re.search(r"(?i)\b(budget|forecast|afford|total|rent|living|bajet|unjuran)\b|বাজেট|পূর্বাভাস|预算|預算", text)
    if not personal or not tuition or broader:
        return None
    value = profile_loader()
    base = {
        "status": "ok", "kind": "personal_fee", "mode": "profile", "calls": [],
        "review": "Authenticated saved-profile lookup; no LLM invoked.",
    }
    if not value:
        return {**base, "facts": None}
    try:
        profile = StudentProfile.model_validate(value)
    except ValueError:
        raise FinanceError("The saved profile needs correction. Open My Student Profile and verify its fields.") from None
    return {
        **base,
        "facts": {
            "amount": major(minor(profile.tuition.amount, profile.tuition.currency), profile.tuition.currency),
            "currency": profile.tuition.currency,
            "due_date": profile.next_tuition_date.isoformat(),
            "fee_period": profile.fee_period,
            "billing_interval_months": profile.billing_interval_months,
        },
    }


LABELS = {
    "en": {
        "title": "Your saved tuition details",
        "amount": "Tuition amount per declared fee period",
        "date": "Saved next unpaid due date",
        "period": "Declared fee period",
        "interval": "Billing interval in months",
        "missing": "Save your tuition amount, currency and next unpaid due date in My Student Profile first.",
        "source": "From your saved profile; no LLM was used and no profile data was sent to Groq for this answer.",
        "verify": "This shows your recorded next unpaid bill. Check the university invoice for the current amount, deadline and payment status. It does not infer a later semester or mark a bill as paid.",
        "semester": "Semester", "year": "Year", "trimester": "Trimester",
        "programme": "Whole programme", "invoice": "One invoice",
    },
    "bn": {
        "title": "আপনার সংরক্ষিত টিউশন তথ্য",
        "amount": "ঘোষিত fee period-এর টিউশন ফি",
        "date": "সংরক্ষিত পরবর্তী অপরিশোধিত ফি দেওয়ার তারিখ",
        "period": "ঘোষিত fee period",
        "interval": "কত মাস পরপর বিল হয়",
        "missing": "আগে My Student Profile-এ টিউশন ফি, মুদ্রা এবং পরবর্তী অপরিশোধিত ফি দেওয়ার তারিখ সংরক্ষণ করুন।",
        "source": "নিজের saved profile থেকে নেওয়া; এই উত্তরে LLM ব্যবহার হয়নি এবং profile-এর তথ্য Groq-এ পাঠানো হয়নি।",
        "verify": "এটি আপনার সংরক্ষিত পরবর্তী অপরিশোধিত বিল। বর্তমান পরিমাণ, শেষ তারিখ ও payment status বিশ্ববিদ্যালয়ের invoice দিয়ে মিলিয়ে নিন। পরের কোনো semester-এর তথ্য অনুমান বা bill paid হিসেবে চিহ্নিত করা হয় না।",
        "semester": "সেমিস্টার", "year": "বছর", "trimester": "ট্রাইমেস্টার",
        "programme": "সম্পূর্ণ programme", "invoice": "একটি invoice",
    },
    "zh": {
        "title": "您保存的学费信息", "amount": "每个申报缴费周期的学费",
        "date": "保存的下一笔未缴学费截止日期", "period": "申报缴费周期",
        "interval": "缴费间隔（月）", "missing": "请先在学生资料中保存学费、币种及下一笔未缴学费的截止日期。",
        "source": "来自您保存的资料；此回答未使用大语言模型，也未向 Groq 发送资料。",
        "verify": "此处显示您记录的下一笔未缴费用。请以大学账单核实当前金额、截止日期和付款状态。系统不会推断之后学期的费用或将账单标记为已付款。",
        "semester": "学期", "year": "学年", "trimester": "三学期制学期",
        "programme": "整个课程", "invoice": "单张账单",
    },
    "ms": {
        "title": "Butiran yuran pengajian tersimpan", "amount": "Yuran bagi setiap tempoh yang diisytiharkan",
        "date": "Tarikh akhir bil belum dibayar yang disimpan", "period": "Tempoh yuran diisytiharkan",
        "interval": "Selang bil dalam bulan", "missing": "Simpan amaun yuran, mata wang dan tarikh akhir bil belum dibayar dalam Profil Pelajar Saya dahulu.",
        "source": "Daripada profil tersimpan anda; tiada LLM digunakan dan tiada data profil dihantar kepada Groq untuk jawapan ini.",
        "verify": "Ini menunjukkan bil belum dibayar seterusnya yang anda rekodkan. Sahkan amaun, tarikh akhir dan status bayaran melalui invois universiti. Sistem tidak menganggar semester kemudian atau menandakan bil telah dibayar.",
        "semester": "Semester", "year": "Tahun", "trimester": "Trimester",
        "programme": "Seluruh program", "invoice": "Satu invois",
    },
}


def render_personal_fee(st, language, answer):
    """Use fixed translated labels; no generated prose or untrusted markup."""
    labels = LABELS.get(language, LABELS["en"])
    facts = answer["facts"]
    if facts is None:
        st.info(labels["missing"])
        return
    st.subheader(labels["title"])
    st.metric(labels["amount"], facts["amount"] + " " + facts["currency"])
    st.write(labels["date"] + ": " + facts["due_date"])
    st.write(labels["period"] + ": " + labels[facts["fee_period"]])
    if facts["billing_interval_months"]:
        st.write(labels["interval"] + ": " + str(facts["billing_interval_months"]))
    st.caption(labels["source"])
    st.info(labels["verify"])
