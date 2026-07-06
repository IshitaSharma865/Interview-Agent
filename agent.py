def create_initial_state(role, experience):
    return {
        "role": role,
        "experience": experience,
        "current_round": "technical",
        "round_number": 1,
        "questions_asked": [],
        "all_questions": [],
        "answers_given": [],
        "scores": [],
        "weak_areas": [],
        "max_questions_per_round": {
            "technical": 5,
            "hr": 3,
            "case_study": 1
        }
    }


def build_evaluator_prompt(role, round_name, question, answer, experience):
    return f"""You are an honest interviewer evaluating a {experience} candidate 
applying for a {role} position.

Question: {question}
Candidate's Answer: {answer}

Scoring guide:
- 1-2: Answer is completely blank, gibberish, or a single letter/word with no meaning (e.g. "k", "idk", "ok")
- 3-4: Answer is attempted but very vague, incomplete, or mostly incorrect
- 5-6: Basic correct answer, acceptable for a {experience} candidate
- 7-8: Clear, well-explained answer with some depth
- 9-10: Excellent answer with examples, strong understanding

Be honest. Do not give pity points. A non-answer must score 1-2.

Respond ONLY in this exact JSON format, nothing else:
{{
    "score": <number from 1-10>,
    "feedback": "<two to three sentence constructive feedback mentioning what was good and what could be improved>",
    "weak_area": "<topic name if score is below 5, otherwise null>"
}}"""

def build_feedback_report_prompt(role, experience, questions_asked_all, answers_given, scores, weak_areas):
    return f"""You just finished interviewing a {experience} candidate for a {role} position.

Here is the full session data:
Questions and Answers with Scores:
{list(zip(questions_asked_all, answers_given, scores))}

Weak areas flagged: {weak_areas}

Generate a structured feedback report in this exact format:

Overall Score: <average score>/10

Strong Areas:
- <point 1>
- <point 2>

Weak Areas:
- <point 1>
- <point 2>

Suggestions for Improvement:
1. <suggestion 1>
2. <suggestion 2>
3. <suggestion 3>

Keep it calibrated to a {experience} candidate. Be encouraging but honest."""

import pdfplumber

def extract_resume_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
def create_initial_state(role, experience):
    return {
        "role": role,
        "experience": experience,
        "current_round": "technical",
        "round_number": 1,
        "questions_asked": [],
        "all_questions": [],
        "answers_given": [],
        "scores": [],
        "weak_areas": [],
        "resume_text": "",
        "max_questions_per_round": {
            "technical": 5,
            "hr": 3,
            "case_study": 1
        }
    }