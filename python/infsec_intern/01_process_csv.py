import csv
import os
import re
import random
import string

'''
Vacancy: https://yandex.ru/jobs/vacancies/interns/infsec_intern/

Напишите на Python программу, которая:
    разобьет информацию в CSV-файле на две ключевые колонки;
    отфильтрует все строки, где значение в столбце N не является логином пользователя.

Требования к логину пользователя:
    состоит только из строчных букв, цифр и символа «-»;
    начинается с буквы;
    не заканчивается на символ «-»;
    имеет длину от 3 до 15 символов.
'''


class ProcessCSV:
    def __init__(self, in_csv, out_csv, columns=None, filter_by_column=None):
        self.in_csv = in_csv
        self.out_csv = out_csv
        self.columns = columns or (1, 4)
        self.filter_by_column = filter_by_column or 1

        if not os.path.exists(self.in_csv):
            print('No dataset found. Generating new random data to work with...')
            ProcessCSV.generate_random_data(self.in_csv, num=2_000)

    def run(self):
        with open(self.in_csv, 'r') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)

            filtered_data = filter(lambda row: self.is_valid_login(row[self.filter_by_column]), list(reader))

        with open(self.out_csv, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            headers = [headers[column] for column in self.columns]
            writer.writerow(headers)

            for filtered_rows_count, filtered_row in enumerate(filtered_data, start=1):
                row = [filtered_row[column] for column in self.columns]
                writer.writerow(row)

        print(f'{filtered_rows_count} rows were successfully filtered and written to {self.out_csv}')

    def is_valid_login(self, login):
        ''' Validates user's login with the simplest way possible

        1st char is a exactly one letter
          chars in between are: letters, digits or dash (up to 13 chars)
        15th (last) char is exactly one letter or digit

        Total login length is: 3-15 chars.

        :param login: login to validate
        '''
        return re.match('^[a-zA-Z]{1}[a-zA-Z0-9-]{1,13}[a-zA-Z0-9]{1}$', login)

    @staticmethod
    def generate_random_data(out_csv, num=100, force=False):
        ''' Generates initial random data to work with.

        :param out_csv: path to the CSV-file to be generated
        :param num: number of rows to be generated
        :param force: force generation if file has already been generated
        '''
        first_name_list = ['Chad', 'Julia', 'Jeremy', 'Amanda', 'Dennis', 'Darrell', 'Roy', 'Winifred', 'Mattie', 'Betty',
                           'Steve', 'Charles', 'Mable', 'Lena', 'Blake', 'Elijah', 'Beatrice', 'Francis', 'Maggie', 'Gordon', ]

        second_name_list = ['Weber', 'Yates', 'Watkins', 'Maldonado', 'Dean', 'Terry', 'Copeland', 'Stanley', 'Mendez', 'Delgado',
                            'Goodwin', 'Willis', 'Shaw', 'Pope', 'McDonald', 'Mullins', 'Ryan', 'Schultz', 'Bradley', 'Hardy', ]

        if not force and os.path.exists(out_csv):
            print('Data is already generated.')
            return

        with open(out_csv, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['id', 'login', 'first_name', 'second_name', 'ip_address'])

            for seq, _ in enumerate(range(num), start=1):
                row = []

                first_name = random.choice(first_name_list)
                second_name = random.choice(second_name_list)

                login_prefix = random.choice("01234567890!@$%&*_-") if random.random() < 0.1 else ""
                login_suffix = random.choice('-_.') if random.random() < 0.1 else ""
                garbage = '-' + ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 10)))
                login_extender = garbage if random.random() < 0.15 else ""

                login = login_prefix + first_name[0] + second_name + login_extender + login_suffix

                ip = ".".join(str(random.randrange(1, 254)) for _ in range(4))

                row.append(seq)
                row.append(login)
                row.append(first_name)
                row.append(second_name)
                row.append(ip)

                writer.writerow(row)

            print(f'{seq} lines were successfully written to {out_csv}.')


def main():
    IN_CSV = os.path.join(os.path.dirname(__file__), 'random-data.csv')
    OUT_CSV = os.path.join(os.path.dirname(__file__), 'filtered-data.csv')

    # Generate initial random date to work with
    # ProcessCSV.generate_random_data(IN_CSV, num=2000, force=True)

    # Two main columns are: 1 and 4 (login and ip_address)
    # Colunmn with user's login is 1
    processor = ProcessCSV(IN_CSV, OUT_CSV, columns=(1, 4), filter_by_column=1)
    processor.run()


if __name__ == '__main__':
    main()
