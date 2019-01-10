import csv
import os
import time


ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_FILE_PATH = 'sample_data/answer.csv'
QUESTION_FILE_PATH = 'sample_data/question.csv'



def read_from_csv(file=QUESTION_FILE_PATH, id=None):
    list_of_data = []
    with open(file) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            data = dict(row)
            if id is not None and row['id'] == id:
                return data
            list_of_data.append(data)
        return list_of_data


def write_to_csv(message, file=QUESTION_FILE_PATH, is_new=True):
    old_message = read_from_csv(file)
    if file == QUESTION_FILE_PATH:
        header = QUESTIONS_HEADER
    else:
        header = ANSWERS_HEADER

    with open(file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for row in old_message:
            if not is_new:
                if message['id'] == row['id']:
                    row = message
            writer.writerow(row)
        if is_new:
            writer.writerow(message)


def generate_id(file=QUESTION_FILE_PATH):
    list_of_messages = read_from_csv(file)
    if len(list_of_messages) == 0:
        new_id = '1'
        return new_id
    max_id = 0
    for row in list_of_messages:
        if int(row['id']) > max_id:
            max_id = int(row['id'])
    new_id = str(max_id + 1)
    return new_id


def collect_data(recieved_data, header=QUESTIONS_HEADER):
    if header == QUESTIONS_HEADER:
        file = QUESTION_FILE_PATH
    else:
        file = ANSWER_FILE_PATH
    message = {key: "" for key in header}
    for key in recieved_data: #TODO more specific code
        message[key] = recieved_data[key]
    message['id'] = generate_id(file)
    message['submission_time'] = time.time()
    return message


def get_time():
    return time.time()


def overwrite_old_csv(new_data, file=QUESTION_FILE_PATH):
    """Can be used to overwrite the whole csv with the new data,
        for example when you want to delete a row from the csv.

        Args:
        new_data(list of dictionaries): contains the new data
        file(str): name of file to overwrite
        """

    if file == QUESTION_FILE_PATH:
        header = QUESTIONS_HEADER
    else:
        header = ANSWERS_HEADER

    with open(file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for row in new_data:
            writer.writerow(row)


def find_answer_id(question_id, file=ANSWER_FILE_PATH):
    """Finds the IDs of the answers which belong to the given question

        Args:
        question_id(str): ID of the given question
        file(str): name of file which contains the answers

        Returns: list of strings"""

    answer_ids = []
    answer_reader = read_from_csv(file)

    for row in answer_reader:
        if row['question_id'] == question_id:
            answer_ids.append(row['id'])
    return answer_ids

