import time
from parser.parser import Controller


if __name__ == '__main__':
    controller = Controller()
    start_time = time.time()
    last_time = start_time
    check_counter = 0
    while True:
        controller.check()
        check_counter += 1
        current_time = time.time()
        print('Время выполнения последней итерации: ' +
              f'{str((current_time - last_time)):.{10}}' + ' секунд')
        if check_counter % 50 == 0:
            print('Среднее время выполнения за [' +
                  str(check_counter) + '] итераций: ' +
                  f'{str((current_time - start_time) / check_counter):.{10}}' + ' секунд')
        last_time = current_time
