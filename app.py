import requests
import os
import json
from dotenv import load_dotenv
import streamlit as st

# --- Streamlit UI ---
st.set_page_config(page_title="Smart MedHelper", layout="centered")

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# --- Load Symptom Database ---
with open("symptom_db.json", "r", encoding="utf-8") as f:
    symptom_db = json.load(f)

# --- Language Settings ---
if 'language' not in st.session_state:
    st.session_state.language = 'Arabic'  # Default language

def toggle_language():
    st.session_state.language = 'Arabic' if st.session_state.language == 'English' else 'English'

# Inject better RTL support when Arabic is selected
if 'language' in st.session_state and st.session_state.language == 'Arabic':
    st.markdown("""
        <style>
            .stApp {
                direction: rtl !important;
                text-align: right !important;
            }
            textarea, input, .stTextInput > div > input, .stTextArea > div > textarea {
                direction: rtl !important;
                text-align: right !important;
            }
            .css-1cpxqw2, .css-10trblm, .stText, .stHeader {
                text-align: right !important;
            }
            label, h1, h2, h3, h4, h5, h6, p {
                text-align: right !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- DeepSeek API Call ---
def query_deepseek(prompt, temperature=0.6):
    if not api_key:
        return "🔴 Error: No API Key found."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"🔴 API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🔴 Request Failed: {str(e)}"

# --- Local DB Lookup ---
def check_local_symptom_db(symptoms_input):
    normalized_input = symptoms_input.lower().replace("،", ",").strip()
    for key in symptom_db:
        if all(symptom.strip() in normalized_input for symptom in key.split(",")):
            entry = symptom_db[key]
            lang = st.session_state.language
            if lang == 'English':
                return f"""
### ✅ Evidence-Based Result (from trusted sources)

**Likely Conditions:**
- {', '.join(entry['conditions'])}

**Urgency:** {entry['triage']}
**Care Tips:** {entry['tips']}
**Sources:** {', '.join(entry['sources'])}
"""
            else:
                return f"""
### ✅ نتيجة معتمدة (من مصادر طبية)

**الأسباب المحتملة:**
- {'، '.join(entry['conditions'])}

**درجة الخطورة:** {entry['triage']}
**نصائح الرعاية:** {entry['tips']}
**المصادر:** {', '.join(entry['sources'])}
"""
    return None

# --- AI Symptom Analyzer ---
def analyze_symptoms(symptoms):
    if st.session_state.language == 'Arabic':
        prompt = f"""
كن مساعدًا طبيًا. حلل هذه الأعراض: "{symptoms}".

أجب بهذا الشكل المحدد:

### مستوى الخطورة:
[🆘 طارئ] / [⚠️ يحتاج مراقبة] / [✅ طبيعي]

### الأسباب المحتملة:
- سبب 1
- سبب 2

### الإجراء الموصى به:
[للحالات الطارئة]: "اطلب الرعاية الطبية فورًا بسبب: [الأعراض الخطيرة]"
[للمراقبة]: "راجع الطبيب خلال X أيام إذا: [علامات التحذير]"
[للحالات الطبيعية]: "الرعاية الذاتية: [النصائح]. المتوقع أن تتحسن خلال X أيام."

### ملاحظة:
"هذا ليس تشخيصًا. استشر طبيبًا إذا استمرت الأعراض."
"""
    else:
        prompt = f"""
As a medical triage assistant, analyze these symptoms: "{symptoms}".

Respond in this EXACT format:

### 🚨 Urgency Level:
[🆘 EMERGENCY] / [⚠️ Monitor] / [✅ Normal]

### 📋 Likely Causes:
- Possible condition 1
- Possible condition 2

### 🩺 Recommended Action:
[For EMERGENCY]: "Seek IMMEDIATE care for: [specific symptoms]"
[For Monitor]: "See a doctor within X days if: [warning signs]"
[For Normal]: "Self-care: [advice]. Should improve in X days."

### ℹ️ Note:
"This is not a diagnosis. Consult a doctor for persistent symptoms."
"""
    return query_deepseek(prompt, temperature=0.3)



# Header & Language Toggle
cols = st.columns([4, 1])
with cols[0]:
    st.title("Smart MedHelper 🩺" if st.session_state.language == 'English' else "المساعد الطبي الذكي 🩺")
with cols[1]:
    st.button("عربي / English", 
              on_click=toggle_language,
              key="lang_toggle",
              help="Switch language",
              use_container_width=True,
              type="primary")

# --- Symptom Checker ---
if st.session_state.language == 'English':
    st.header("Symptom Checker 🤒")
    symptom_text = "Describe your symptoms (e.g., chest pain, fever, headache):"
    analyze_text = "Analyze Symptoms"
    warning_text = "⚠️ Please describe your symptoms."
else:
    st.header("فحص الأعراض 🤒")
    symptom_text = "صف أعراضك (مثل ألم الصدر، حمى، صداع):"
    analyze_text = "تحليل الأعراض"
    warning_text = "⚠️ يرجى وصف الأعراض"

symptoms = st.text_area(symptom_text)

if st.button(analyze_text):
    if symptoms.strip():
        with st.spinner("🔍 Analyzing..." if st.session_state.language == 'English' else "🔍 جاري التحليل..."):
            local_result = check_local_symptom_db(symptoms)
            analysis = local_result if local_result else analyze_symptoms(symptoms)

            if "🆘" in analysis or "طارئ" in analysis:
                st.error(analysis)
            elif "⚠️" in analysis or "مراقبة" in analysis:
                st.warning(analysis)
            else:
                st.success(analysis)
    else:
        st.warning(warning_text)

# --- Drug Interaction Checker ---
if st.session_state.language == 'English':
    st.header("Drug Interaction Checker 💊")
    drug_text = "Enter medications (comma-separated):"
    check_text = "Check Interactions"
    drug_warning = "⚠️ Enter at least 2 medications."
else:
    st.header("فحص التفاعلات الدوائية 💊")
    drug_text = "أدخل الأدوية (مفصولة بفواصل):"
    check_text = "فحص التفاعلات"
    drug_warning = "⚠️ أدخل دوائين على الأقل."

drugs = st.text_input(drug_text)

if st.button(check_text):
    if drugs:
        with st.spinner("🔍 Checking..." if st.session_state.language == 'English' else "🔍 جاري الفحص..."):
            if st.session_state.language == 'Arabic':
                prompt = f"كن صيدليًا. افحص التفاعلات بين: {drugs}. اشرح المخاطر بلغة بسيطة."
            else:
                prompt = f"Act as a pharmacist. Check interactions between: {drugs}. Explain risks in simple terms."
            response = query_deepseek(prompt, temperature=0.5)
            st.markdown(response)
    else:
        st.warning(drug_warning)
