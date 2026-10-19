"""Display-only examples. Placeholders never supply calculation values."""

# Keep these separate from widget values so translating an example cannot
# replace a saved profile field or alter a financial input.
HINTS = {
    "email": (
        "you@example.com",
        "আপনার account-এর email",
        "您的账户邮箱",
        "E-mel akaun anda",
    ),
    "username": (
        "Enter your username",
        "আপনার username লিখুন",
        "输入用户名",
        "Masukkan nama pengguna",
    ),
    "password": (
        "Enter your password",
        "আপনার password লিখুন",
        "输入密码",
        "Masukkan kata laluan",
    ),
    "new_password": (
        "Choose at least 12 characters",
        "অন্তত ১২ অক্ষরের password দিন",
        "至少 12 个字符",
        "Pilih sekurang-kurangnya 12 aksara",
    ),
    "repeat_password": (
        "Re-enter the same password",
        "একই password আবার লিখুন",
        "再次输入相同密码",
        "Masukkan semula kata laluan yang sama",
    ),
    "amount": (
        "e.g. 100",
        "যেমন: 100",
        "例如：100",
        "cth. 100",
    ),
    "percent": (
        "e.g. 10",
        "যেমন: 10",
        "例如：10",
        "cth. 10",
    ),
    "university": (
        "e.g. Universiti Kebangsaan Malaysia",
        "যেমন: Universiti Kebangsaan Malaysia",
        "例如：Universiti Kebangsaan Malaysia",
        "cth. Universiti Kebangsaan Malaysia",
    ),
    "campus": (
        "e.g. Bangi campus",
        "যেমন: Bangi campus",
        "例如：Bangi 校区",
        "cth. Kampus Bangi",
    ),
    "department": (
        "e.g. Faculty of Engineering",
        "যেমন: Faculty of Engineering",
        "例如：工程学院",
        "cth. Fakulti Kejuruteraan",
    ),
    "programme": (
        "e.g. Master of Science",
        "যেমন: Master of Science",
        "例如：理学硕士",
        "cth. Sarjana Sains",
    ),
    "study_mode": (
        "e.g. Research / Coursework",
        "যেমন: Research / Coursework",
        "例如：研究型 / 授课型",
        "cth. Penyelidikan / Kerja kursus",
    ),
    "city": (
        "e.g. Bangi",
        "যেমন: Bangi",
        "例如：Bangi",
        "cth. Bangi",
    ),
    "country": (
        "e.g. Malaysia",
        "যেমন: Malaysia",
        "例如：马来西亚",
        "cth. Malaysia",
    ),
    "note": (
        "e.g. Reference to your latest tuition invoice",
        "যেমন: সর্বশেষ tuition invoice-এর reference",
        "例如：最新学费账单的依据",
        "cth. Rujukan invois yuran terkini",
    ),
    "model": (
        "Enter the exact model ID",
        "সঠিক model ID লিখুন",
        "输入准确的模型 ID",
        "Masukkan ID model yang tepat",
    ),
    "confirmation": (
        "Type the six characters shown above",
        "উপরে দেখানো ছয় অক্ষর লিখুন",
        "输入上方显示的六个字符",
        "Taip enam aksara yang dipaparkan di atas",
    ),
}


def hint(translator, key):
    """Return a translated placeholder, falling back to the English copy."""
    index = {"en": 0, "bn": 1, "zh": 2, "ms": 3}.get(translator.language, 0)
    return HINTS[key][index]
