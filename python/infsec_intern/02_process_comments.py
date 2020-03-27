import csv
import json
import os
import urllib.request

'''
Vacancy: https://yandex.ru/jobs/vacancies/interns/infsec_intern/

Выгрузите из API, доступного по ссылке (https://jsonplaceholder.typicode.com/comments),
все комментарии, в которых:
- значение в поле email заканчивается на .info;
- количество слов в поле name меньше 4.

Создайте файл в формате CSV, в котором распределите информацию из комментариев на две колонки следующим образом:
- email — значения поля email;
- words_count — количество слов из поля name.
'''


def load_filtered_json_data(json_url):
    ''' Loads raw json data from the given URL and filters it according to the requirements

    :param json_url: URL to the json-dataset
    '''
    filtered_data = []

    try:
        with urllib.request.urlopen(json_url) as url:
            data = json.loads(url.read().decode())

            for obj_count, obj in enumerate(data, start=1):
                if is_vaid_object(obj):
                    email = obj['email']
                    word_count = len(obj['name'].split())

                    row = email, word_count
                    filtered_data.append(row)

            print(f'{obj_count} json objects were successfully processed.')

    except urllib.error.URLError as err:
        print(f'An error occured: {err}')

    finally:
        return filtered_data


def save_csv_data(data, out_file):
    ''' Saves data filtered by `load_filtered_json_data` function to a CSV-file.

    :param data: data, filtered by `load_filtered_json_data` function
    :param out_file: path to the CSV-file to be saved
    '''
    try:
        with open(out_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['email', 'words_count'])

            for rows_count, row in enumerate(data, start=1):
                writer.writerow(row)

            print(f'{rows_count} lines were successfully written to {out_file}.')

    except OSError as err:
        print(f'An error occured: {err}')


def is_vaid_object(json_object):
    ''' Checks if given json object is valid

    :param json_object: json object
    '''
    name, email = json_object['name'], json_object['email']

    return email.endswith('.info') and len(name.split()) in range(4)


def main():
    URL = 'https://jsonplaceholder.typicode.com/comments'
    OUT_CSV = os.path.join(os.path.dirname(__file__), 'json-filtered-data.csv')

    filtered_data = load_filtered_json_data(json_url=URL)

    if not filtered_data:
        print('No data to process. Exiting...')
    else:
        save_csv_data(data=filtered_data, out_file=OUT_CSV)


if __name__ == '__main__':
    main()
