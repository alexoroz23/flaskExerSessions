from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def show_survey_start():
    """Select a survey."""
    # Render survey_start.html template with survey object
    return render_template("survey_start.html", survey=survey)

@app.route("/start", methods=["POST"])
def start_survey():
    """Clear the session of responses."""
    # Clear session of responses by setting empty list
    session[RESPONSES_KEY] = []
    # Redirect user to first question
    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""
    # Get user's choice from form
    choice = request.form['answer']
    # Get user's previous responses from session
    responses = session[RESPONSES_KEY]
    # Append user's new response to previous responses
    responses.append(choice)
    # Update user's responses in session
    session[RESPONSES_KEY] = responses
    # If all questions answered, redirect to completion page
    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    # Otherwise, redirect to next question
    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    # Get user's previous responses from session
    responses = session.get(RESPONSES_KEY)
    # If session expired, redirect to start of survey
    if (responses is None):
        return redirect("/")
    # If all questions answered, redirect to completion page
    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    # If user skipped a question or question is invalid, redirect to previous question and flash error message
    if (len(responses) != qid):
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")
    # Get current question from survey object
    question = survey.questions[qid]
    # Render question.html template with current question and its number
    return render_template(
        "question.html", question_num=qid, question=question)

@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""
    # Render completion.html template
    return render_template("completion.html")