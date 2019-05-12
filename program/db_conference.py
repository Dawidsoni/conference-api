import sys
from query_handler import QueryHandler


def process_input(query_handler):
    while True:
        input_line = sys.stdin.readline()
        if not input_line:
            break
        print(query_handler.handle_query(input_line))


def main():
    try:
        query_handler = QueryHandler()
        process_input(query_handler)
    except Exception as exc:
        print(exc)


main()

