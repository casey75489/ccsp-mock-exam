import streamlit as st
import json
import os
import random
import time

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="CCSP Bilingual Exam Portal",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism & Dark styling overrides)
st.markdown("""
<style>
    .domain-tag {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .option-text {
        font-size: 1rem;
        margin-bottom: 0.2rem;
    }
    .translation-sub {
        font-size: 0.9rem;
        color: #9ca3af;
        font-style: normal;
    }
    .badge-pass {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        display: inline-block;
    }
    .badge-fail {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        display: inline-block;
    }
    .review-card {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
    .correct-border {
        border-left: 4px solid #10b981;
    }
    .incorrect-border {
        border-left: 4px solid #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# Helper to load the database
@st.cache_data
def load_questions_db():
    db_path = os.path.join(os.path.dirname(__file__), "questions.json")
    if not os.path.exists(db_path):
        return []
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Domain mapping dictionary
domains_map = {
    1: "Domain 1: Cloud Concepts, Architecture and Design",
    2: "Domain 2: Cloud Data Security",
    3: "Domain 3: Cloud Platform and Infrastructure Security",
    4: "Domain 4: Cloud Application Security",
    5: "Domain 5: Cloud Security Operations",
    6: "Domain 6: Legal, Risk and Compliance"
}

all_questions = load_questions_db()

# Initialize session state variables
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "session_questions" not in st.session_state:
    st.session_state.session_questions = []
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "flagged" not in st.session_state:
    st.session_state.flagged = set()
if "mode" not in st.session_state:
    st.session_state.mode = "exam"
if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "time_spent_stored" not in st.session_state:
    st.session_state.time_spent_stored = 0

def start_new_quiz(mode_selection):
    if not all_questions:
        st.error("找不到題目資料庫 questions.json，請確認檔案位置。")
        return
        
    shuffled = list(all_questions)
    random.shuffle(shuffled)
    
    st.session_state.session_questions = shuffled[:150]
    st.session_state.session_questions.sort(key=lambda x: x["id"]) # Sort by ID for reference consistency
    st.session_state.current_idx = 0
    st.session_state.user_answers = {}
    st.session_state.flagged = set()
    st.session_state.mode = mode_selection
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.session_state.time_spent_stored = 0
    st.session_state.quiz_active = True

def parse_bilingual(text):
    """Splits the database bilingual format back into parts if needed, or renders it nicely."""
    if not text:
        return "", ""
    parts = text.split("\n*(简中翻译：")
    english = parts[0]
    chinese = parts[1].replace(")*", "") if len(parts) > 1 else ""
    return english, chinese

def parse_option_bilingual(option_text):
    if not option_text:
        return "", ""
    parts = option_text.split(" / *(")
    english = parts[0]
    chinese = parts[1].replace(")*", "") if len(parts) > 1 else ""
    return english, chinese

# --- Welcome Screen ---
if not st.session_state.quiz_active:
    st.title("🔒 CCSP 模擬考試與練習系統 (Bilingual Portal)")
    st.write(f"歡迎來到資深 CCSP 認證輔導與練習平台。本系統資料庫包含 **{len(all_questions)}** 題高品質單選題，每次測驗將隨機抽選 **150** 題獨立不重複的題目。")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 模擬考試模式 (Exam Mode)")
        st.markdown("""
        * **限時 3 小時 (180 分鐘)**
        * 模擬真實考試，作答期間**不會**顯示即時答案與解析
        * 適合檢測自身實力與答題配速
        * 提交後提供詳細的六大網域弱點分析與所有錯題解析
        """)
        if st.button("啟動模擬考試模式", type="primary", use_container_width=True):
            start_new_quiz("exam")
            st.rerun()
            
    with col2:
        st.subheader("📖 即時練習模式 (Practice Mode)")
        st.markdown("""
        * **無時間限制**
        * 每做完一題，系統將**立即顯示**該題的對錯判定及詳細觀念解析
        * 適合一題題細細研讀、打底與加強記憶
        * 答錯的選項有明確標記，幫助釐清觀念
        """)
        if st.button("啟動即時練習模式", use_container_width=True):
            start_new_quiz("practice")
            st.rerun()

# --- Quiz Interface (Not Submitted) ---
elif st.session_state.quiz_active and not st.session_state.submitted:
    q_list = st.session_state.session_questions
    idx = st.session_state.current_idx
    q = q_list[idx]
    
    # Calculate elapsed time
    elapsed_seconds = int(time.time() - st.session_state.start_time)
    
    # Render Sidebar
    with st.sidebar:
        st.subheader("📋 測驗進度 (Progress)")
        
        # Display Mode badge
        if st.session_state.mode == "exam":
            st.markdown("<span style='color:#f59e0b; font-weight:700;'>🏆 模擬考試模式</span>", unsafe_allow_html=True)
            time_left = max(0, 3 * 3600 - elapsed_seconds)
            hrs_left = time_left // 3600
            mins_left = (time_left % 3600) // 60
            secs_left = time_left % 60
            
            # Highlight warning if less than 30 mins
            timer_color = "red" if time_left <= 30 * 60 else "white"
            st.markdown(f"⏱️ 剩餘時間：<span style='color:{timer_color}; font-weight:bold; font-size:1.2rem;'>{hrs_left:02d}:{mins_left:02d}:{secs_left:02d}</span>", unsafe_allow_html=True)
            if time_left == 0:
                st.session_state.time_spent_stored = 3 * 3600
                st.session_state.submitted = True
                st.rerun()
        else:
            st.markdown("<span style='color:#10b981; font-weight:700;'>📖 即時練習模式</span>", unsafe_allow_html=True)
            hrs_spent = elapsed_seconds // 3600
            mins_spent = (elapsed_seconds % 3600) // 60
            secs_spent = elapsed_seconds % 60
            st.markdown(f"⏱️ 已用時間：`{hrs_spent:02d}:{mins_spent:02d}:{secs_spent:02d}`")
            
        # Progress Bar
        progress_val = (idx + 1) / len(q_list)
        st.progress(progress_val)
        st.write(f"題號：**{idx + 1}** / {len(q_list)}")
        
        st.write("---")
        st.write("🎯 **題號快速導覽地圖**")
        
        # Grid layout for navigation (10 columns)
        cols_nav = st.columns(10)
        for i in range(len(q_list)):
            col_idx = i % 10
            btn_label = f"{i+1}"
            
            # Style based on status (flagged, answered, current)
            is_flagged = i in st.session_state.flagged
            is_answered = i in st.session_state.user_answers
            
            emoji = ""
            if is_flagged:
                emoji = "🚩"
            elif is_answered:
                emoji = "✏️"
                
            btn_key = f"nav_btn_{i}_{emoji}"
            # Render small button
            if cols_nav[col_idx].button(f"{btn_label}{emoji}", key=btn_key):
                st.session_state.current_idx = i
                st.rerun()
                
        st.write("---")
        if st.button("🚨 提前提交試卷", type="primary", use_container_width=True):
            unanswered = len(q_list) - len(st.session_state.user_answers)
            if unanswered > 0:
                st.warning(f"您還有 {unanswered} 題尚未作答！")
            if st.checkbox("我確認已填寫完畢，要送出評分。"):
                st.session_state.time_spent_stored = elapsed_seconds
                st.session_state.submitted = True
                st.rerun()
                
        if st.button("🚪 放棄並返回首頁", use_container_width=True):
            st.session_state.quiz_active = False
            st.rerun()

    # Main Area quiz container
    eng_q, chi_q = parse_bilingual(q["question"])
    
    st.markdown(f"### Question {idx + 1}")
    st.markdown(f"<span class='domain-tag'>{q['domain']}</span>", unsafe_allow_html=True)
    st.write("")
    
    # Display Question
    st.markdown(f"**{eng_q}**")
    if chi_q:
        st.markdown(f"(简中翻译：{chi_q})")
        
    st.write("---")
    
    # Display Options
    opt_labels = []
    opt_keys = ["A", "B", "C", "D"]
    
    for key in opt_keys:
        eng_opt, chi_opt = parse_option_bilingual(q["options"][key])
        label = f"{key}. {eng_opt}"
        if chi_opt:
            label += f" / ({chi_opt})"
        opt_labels.append(label)
        
    # Get previously selected option index
    prev_ans = st.session_state.user_answers.get(idx, None)
    default_select_idx = opt_keys.index(prev_ans) if prev_ans in opt_keys else None
    
    # Radio Selection
    selected_option_label = st.radio(
        "請選擇您的答案：",
        options=opt_labels,
        index=default_select_idx,
        key=f"q_radio_{idx}",
        label_visibility="collapsed"
    )
    
    # Store answer instantly
    if selected_option_label:
        selected_key = selected_option_label[0] # "A", "B", "C", or "D"
        st.session_state.user_answers[idx] = selected_key
        
    # Check current answer (polled after radio selection updates st.session_state)
    current_ans = st.session_state.user_answers.get(idx, None)
    
    # Practice Mode Feedback Panel
    if st.session_state.mode == "practice" and current_ans:
        st.write("")
        is_correct = current_ans == q["answer"]
        if is_correct:
            st.success("🟢 答對了！ (Correct)")
        else:
            st.error(f"🔴 答錯了！ (Incorrect) 正確答案為：**{q['answer']}**")
            
        eng_exp, chi_exp = parse_bilingual(q["explanation"])
        st.markdown(f"""
        **💡 題目解析 (Explanation)：**
        {eng_exp}
        
        (简中翻译：{chi_exp})
        """)
        
    st.write("---")
    
    # Bottom Navigation Controls
    col_prev, col_flag, col_next = st.columns([1, 1, 1])
    
    with col_prev:
        if st.button("⬅️ 上一題 (Previous)", use_container_width=True, disabled=(idx == 0)):
            st.session_state.current_idx -= 1
            st.rerun()
            
    with col_flag:
        is_already_flagged = idx in st.session_state.flagged
        flag_btn_label = "🚩 取消標記 (Unflag)" if is_already_flagged else "🚩 標記此題 (Flag)"
        if st.button(flag_btn_label, use_container_width=True):
            if is_already_flagged:
                st.session_state.flagged.remove(idx)
            else:
                st.session_state.flagged.add(idx)
            st.rerun()
            
    with col_next:
        if idx == len(q_list) - 1:
            if st.button("✓ 提交試卷 (Submit)", type="primary", use_container_width=True):
                st.session_state.time_spent_stored = elapsed_seconds
                st.session_state.submitted = True
                st.rerun()
        else:
            if st.button("下一題 (Next) ➡️", use_container_width=True):
                st.session_state.current_idx += 1
                st.rerun()

# --- Results Page (Submitted) ---
elif st.session_state.submitted:
    q_list = st.session_state.session_questions
    user_ans = st.session_state.user_answers
    
    correct_count = sum(1 for i, q in enumerate(q_list) if user_ans.get(i) == q["answer"])
    score_percent = round((correct_count / len(q_list)) * 100)
    
    st.title("📊 測驗結算與分析報告")
    
    # Overview Banner
    col_score, col_status = st.columns(2)
    with col_score:
        st.metric(label="最終得分 (Score)", value=f"{score_percent}%", delta=f"{correct_count}/{len(q_list)} 題")
    with col_status:
        if score_percent >= 70:
            st.markdown("<div class='badge-pass'>🎉 恭喜通過！ (PASSED)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='badge-fail'>❌ 未達合格標準 (FAILED)</div>", unsafe_allow_html=True)
            
    # Time spent format
    hrs_spent = st.session_state.time_spent_stored // 3600
    mins_spent = (st.session_state.time_spent_stored % 3600) // 60
    secs_spent = st.session_state.time_spent_stored % 60
    st.write(f"⏱️ 總共花費時間：`{hrs_spent:02d} 小時 {mins_spent:02d} 分鐘 {secs_spent:02d} 秒`")
    st.write("---")
    
    # Domain Breakdown
    st.subheader("📊 六大網域成績分析 (Domain Analysis)")
    
    domain_stats = {}
    for i in range(1, 7):
        domain_stats[i] = {"total": 0, "correct": 0}
        
    for i, q in enumerate(q_list):
        # Extract Domain number
        dom_num = int(q["domain"].split("Domain ")[1].split(":")[0])
        domain_stats[dom_num]["total"] += 1
        if user_ans.get(i) == q["answer"]:
            domain_stats[dom_num]["correct"] += 1
            
    col_d1, col_d2 = st.columns(2)
    for dom_num, stats in domain_stats.items():
        percent = round((stats["correct"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        dom_name = domains_map[dom_num]
        
        target_col = col_d1 if dom_num <= 3 else col_d2
        with target_col:
            st.write(f"**{dom_name}**")
            st.progress(percent / 100)
            st.write(f"答對率：{percent}% ({stats['correct']}/{stats['total']} 題)")
            st.write("")
            
    st.write("---")
    
    # Review & Explanation Section
    st.subheader("🔍 考題回顧與解析")
    
    filter_choice = st.selectbox(
        "篩選條件：",
        ["全部考題", "僅看錯題", "僅看對題", "僅看標記題"]
    )
    
    for i, q in enumerate(q_list):
        u_a = user_ans.get(i)
        is_corr = u_a == q["answer"]
        is_flagged = i in st.session_state.flagged
        
        # Apply filters
        if filter_choice == "僅看錯題" and is_corr:
            continue
        if filter_choice == "僅看對題" and not is_corr:
            continue
        if filter_choice == "僅看標記題" and not is_flagged:
            continue
            
        border_class = "correct-border" if is_corr else "incorrect-border"
        flag_status = "🚩 [已標記]" if is_flagged else ""
        
        eng_q, chi_q = parse_bilingual(q["question"])
        eng_exp, chi_exp = parse_bilingual(q["explanation"])
        
        st.markdown(f"""
        <div class='review-card {border_class}'>
            <strong>Question {i + 1} ({q['domain']}) {flag_status}</strong><br/>
            <span style='color:{"#34d399" if is_corr else "#f87171"}; font-weight:700;'>
                {"答對 (Correct)" if is_corr else "答錯 (Incorrect)"}
            </span><br/><br/>
            <strong>{eng_q}</strong><br/>
            <span class='translation-sub'>(简中翻译：{chi_q})</span><br/><br/>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Options
        for key in ["A", "B", "C", "D"]:
            eng_opt, chi_opt = parse_option_bilingual(q["options"][key])
            prefix = ""
            if key == q["answer"]:
                prefix = "✅ "
            elif key == u_a and not is_corr:
                prefix = "❌ "
                
            st.write(f"{prefix}**{key}.** {eng_opt} / ({chi_opt})")
            
        st.markdown(f"""
        > **💡 解析 (Explanation)：**  
        > {eng_exp}  
        >   
        > (简中翻译：{chi_exp})
        """)
        st.write("---")
        
    if st.button("🔄 重新開始新測驗", type="primary", use_container_width=True):
        st.session_state.quiz_active = False
        st.rerun()
