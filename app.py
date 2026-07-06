import os
import uuid
import json
import random
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from groq import Groq
from werkzeug.utils import secure_filename
from agent import create_initial_state, build_evaluator_prompt, build_feedback_report_prompt, extract_resume_text

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

sessions = {}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_interview():
    data = request.json
    role = data.get("role")
    experience = data.get("experience")

    session_id = str(uuid.uuid4())
    sessions[session_id] = create_initial_state(role, experience)

    return jsonify({
        "session_id": session_id,
        "message": f"Starting your {experience} {role} interview. Let's begin with the technical round."
    })

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    session_id = request.form.get("session_id")
    file = request.files.get("resume")

    if not file or not session_id:
        return jsonify({"error": "Missing file or session."})

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    resume_text = extract_resume_text(file_path)

    state = sessions.get(session_id)
    if state:
        state["resume_text"] = resume_text

    score_prompt = f"""You are an expert resume reviewer evaluating a {state['experience']} candidate
applying for a {state['role']} position. Hold the candidate to standards appropriate for their experience level.
A {state['experience']} candidate is expected to have significant achievements, leadership, measurable impact,
and strong technical depth. Be strict accordingly.

Here is the candidate's resume:

{resume_text}

Give a structured resume review in this exact format:

Resume Score: <number from 1-10>/10

Strong Points:
- <point 1>
- <point 2>

Areas to Improve:
- <point 1>
- <point 2>

Suggestions:
1. <suggestion 1>
2. <suggestion 2>
3. <suggestion 3>

Be honest, specific, and constructive."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": score_prompt}]
    )

    review = response.choices[0].message.content.strip()
    return jsonify({"review": review})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id")

    state = sessions.get(session_id)
    if not state:
        return jsonify({"type": "error", "message": "Session expired. Please refresh and start again."})

    evaluation = None

    if state["questions_asked"]:
        last_question = state["questions_asked"][-1]

        eval_prompt = build_evaluator_prompt(
            state["role"], state["current_round"], last_question, user_message, state["experience"]
        )

        eval_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": eval_prompt}]
        )

        try:
            eval_text = eval_response.choices[0].message.content.strip()
            eval_data = json.loads(eval_text)
        except:
            eval_data = {"score": 3, "feedback": "Your answer was too brief to evaluate properly. Try to elaborate more.", "weak_area": "Communication"}

        state["answers_given"].append(user_message)
        state["scores"].append(eval_data["score"])
        if eval_data.get("weak_area"):
            state["weak_areas"].append(eval_data["weak_area"])

        evaluation = {
            "score": eval_data["score"],
            "feedback": eval_data["feedback"]
        }

    questions_in_round = len(state["questions_asked"])
    max_for_round = state["max_questions_per_round"][state["current_round"]]
    transition_msg = None

    if questions_in_round >= max_for_round:
        if state["current_round"] == "technical":
            state["current_round"] = "hr"
            state["questions_asked"] = []
            transition_msg = "Technical round complete! Moving to the HR round now."
        elif state["current_round"] == "hr":
            state["current_round"] = "case_study"
            state["questions_asked"] = []
            transition_msg = "HR round complete! Moving to the case study round now."
        else:
            report_prompt = build_feedback_report_prompt(
                state["role"], state["experience"],
                state["all_questions"], state["answers_given"],
                state["scores"], state["weak_areas"]
            )
            report_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": report_prompt}]
            )
            report = report_response.choices[0].message.content.strip()
            return jsonify({
                "type": "report",
                "evaluation": evaluation,
                "report": report
            })

    seed = random.randint(1, 10000)

    resume_context = ""
    if state.get("resume_text"):
        resume_context = f"\nThe candidate's resume:\n{state['resume_text']}\nAsk questions relevant to their actual experience and projects where possible."

    system_prompt = f"""You are conducting a {state['current_round']} interview round 
for a {state['experience']} {state['role']} position.
{resume_context}

Questions already asked: {state['questions_asked']}

Rules:
- Ask ONE question only
- Never ask about the same topic twice
- Vary the type of question each time — mix conceptual, practical, scenario-based, and tool-specific questions
- Avoid the most common generic questions like "what is data analysis" or "tell me about yourself" unless absolutely necessary
- Be creative and specific to the {state['role']} role
- Randomness seed for variety: {seed}

Only output the question, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the next question."}
        ]
    )

    question = response.choices[0].message.content.strip()
    state["questions_asked"].append(question)
    state["all_questions"].append(question)

    return jsonify({
        "type": "question",
        "evaluation": evaluation,
        "transition": transition_msg,
        "question": question
    })

if __name__ == "__main__":
    app.run(debug=True)