import streamlit as st
import pdfplumber
from transformers import pipeline

# Load zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Hàm đọc nội dung file
def read_file(file):
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    else:
        text = file.read().decode("utf-8")
    return text

# Hàm phân loại kỹ năng
def classify_skills(text, candidate_labels):
    result = classifier(text, candidate_labels)
    skills_above_threshold = [
        label for label, score in zip(result["labels"], result["scores"]) if score > 0.3
    ]
    return skills_above_threshold

# Giả lập số năm kinh nghiệm
def estimate_experience(text):
    if "5 năm" in text or "five years" in text:
        return 5
    elif "4 năm" in text or "four years" in text:
        return 4
    elif "3 năm" in text or "three years" in text:
        return 3
    else:
        return 1

st.title("🔎 Lọc CV Dựa trên CV Mẫu")

# Upload nhiều CV mẫu
sample_cv_files = st.file_uploader("Upload nhiều CV mẫu (.txt, .pdf)", type=["txt", "pdf"], accept_multiple_files=True)

if sample_cv_files:
    all_sample_skills = []

    # Đọc và phân tích tất cả CV mẫu
    for sample_file in sample_cv_files:
        sample_cv_text = read_file(sample_file)
        
        # Giả định danh sách kỹ năng phổ biến
        candidate_skills = ["Python", "Java", "SQL", "C#", "JavaScript", "AWS", "Docker", "Kubernetes", "React", "Django"]
        sample_skills = classify_skills(sample_cv_text, candidate_skills)
        
        st.write(f"**Kỹ năng rút ra từ CV mẫu {sample_file.name}:** {', '.join(sample_skills)}")
        
        # Kết hợp các kỹ năng từ tất cả các CV mẫu
        all_sample_skills.extend(sample_skills)
    
    # Lọc các kỹ năng trùng lặp và loại bỏ
    all_sample_skills = list(set(all_sample_skills))
else:
    st.warning("Bạn cần upload ít nhất một CV mẫu để tiếp tục.")
    st.stop()

# Upload các CV cần lọc
uploaded_files = st.file_uploader("Upload nhiều CV cần lọc (.txt, .pdf)", accept_multiple_files=True)

cv_data = []

if uploaded_files:
    for file in uploaded_files:
        text = read_file(file)
        detected_skills = classify_skills(text, all_sample_skills)
        experience_years = estimate_experience(text)
        cv_data.append({
            "name": file.name,
            "skills": detected_skills,
            "experience_years": experience_years
        })

    # Lọc theo kỹ năng (ít nhất 1 kỹ năng giống CV mẫu)
    filtered_cvs = [
        cv for cv in cv_data if any(skill in cv["skills"] for skill in all_sample_skills)
    ]

    # Sắp xếp theo kinh nghiệm giảm dần
    sorted_cvs = sorted(filtered_cvs, key=lambda x: x["experience_years"], reverse=True)

    st.subheader("📄 Kết quả lọc:")
    if sorted_cvs:
        for cv in sorted_cvs:
            st.write(f"**Tên file:** {cv['name']}")
            st.write(f"**Kỹ năng trùng khớp:** {', '.join(cv['skills'])}")
            st.write(f"**Kinh nghiệm (ước lượng):** {cv['experience_years']} năm")
            st.write("---")
    else:
        st.warning("Không tìm thấy CV nào phù hợp với các CV mẫu.")
