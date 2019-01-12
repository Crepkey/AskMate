from flask import Flask, render_template, request, redirect, url_for
import data_manager
import util
import copy

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    sorted_messages = util.sort_by_key()
    return render_template('index.html', sorted_messages=sorted_messages)


@app.route('/question/<question_id>')
def get_question_details(question_id):
    """ Input: question_id = string
        Output: render_template with different attributes

        This function collects the questions'/answers' details for the table creating on the question_details.html

        ATTRIBUTES:
            question = {dictionary}
            question_header = {list}
            title = {string}
            answers = {list which has dictionaries}
            answers_header = {list}
            edit_question_url = {string}
        """
    question = data_manager.read_from_csv(id=question_id)
    title = copy.deepcopy(question["title"])
    del question["title"]
    question_header = util.create_header(question)

    all_answers = data_manager.read_from_csv(data_manager.ANSWER_FILE_PATH)
    answers = [answer for answer in all_answers if answer["question_id"] == question_id]
    answers_header = util.create_header(question)

    edit_question_url = url_for('route_edit_question', question_id=question_id)
    return render_template('question_details.html',
                           question=question,
                           question_header=question_header,
                           title=title,
                           answers=answers,
                           answers_header=answers_header,
                           edit_question_url=edit_question_url)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        return render_template('question.html',
                               question_title='',
                               question_message='',
                               page_title="AskMate | Add new question",
                               header="Add a new question",
                               button_text='Submit question'
                               )
    else:
        new_question = {
            'title': request.form.get('title'),
            'message': request.form.get('message')
        }

        # Generating the final dictionary for the new question
        new_question_final = data_manager.collect_data(new_question)

        # Writing the new question to the csv
        data_manager.write_to_csv(new_question_final)

        # Generating the URL for the new question
        question_id = new_question_final['id']
        question_url = url_for('get_question_details', question_id=question_id)

        return redirect(question_url)


@app.route('/question/<question_id>/edit-question', methods=['GET', 'POST'])
def route_edit_question(question_id):
    question = data_manager.read_from_csv(id=question_id)
    if request.method == 'GET':
        question_title = question['title']
        question_message = question['message']
        return render_template('question.html',
                               question_title=question_title,
                               question_message=question_message,
                               page_title="AskMate | Edit question",
                               header="Edit question",
                               button_text='Submit question'
                               )
    else:
        question['title'] = request.form.get('title')
        question['message'] = request.form.get('message')
        question['submission_time'] = data_manager.get_time()
        question_url = url_for('get_question_details', question_id=question_id)
        data_manager.write_to_csv(question, is_new=False)
        return redirect(question_url)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    """
    Add a new answer to the selected question
    on the Question Details page
    Args:
        question_id (string): the ID of the selected question
    Returns:
        question_url (string): the URL back to the selected question
    """
    if request.method == 'GET':
        return render_template('answer.html')
    else:
        new_answer = {'message': request.form.get('answer')}

        # Generating the final dictionary for the new answer
        new_answer_final = data_manager.collect_data(new_answer, header=data_manager.ANSWERS_HEADER)
        new_answer_final['question_id'] = question_id

        # Writing the new answer to the csv
        data_manager.write_to_csv(new_answer_final, data_manager.ANSWER_FILE_PATH)

        # Generating the URL for the question which the answer belongs to
        question_url = url_for('get_question_details', question_id=question_id)

        return redirect(question_url)


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    # Reading all data from question.csv to a list of dictionaries
    question_reader = data_manager.read_from_csv()

    # Deleting the question's dict from the list
    for row in question_reader:
        if row['id'] == question_id:
            question_reader.remove(row)

    # Writing back the list to the csv
    data_manager.overwrite_old_csv(question_reader)

    # Deleting the answers given to that question
    answer_ids = data_manager.find_answer_id(question_id)
    for id in answer_ids:
        delete_answer(id)

    return redirect('/')


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    # Reading all data from answer.csv to a list of dictionaries
    answer_reader = data_manager.read_from_csv(file=data_manager.ANSWER_FILE_PATH)

    # Deleting the answer's dict from the list
    for row in answer_reader:
        if row['id'] == answer_id:
            answer_reader.remove(row)
            question_id = row['question_id']

    # Writing back the list to the csv
    data_manager.overwrite_old_csv(answer_reader, file=data_manager.ANSWER_FILE_PATH)

    question_url = url_for('get_question_details', question_id=question_id)
    return redirect(question_url)


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
