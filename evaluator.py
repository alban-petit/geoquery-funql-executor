from geoquery import evaluate
from parse import parse

def execute(program):
    query = parse(program)
    answer = evaluate(query)
    return answer

def compare(program1, program2):
    answer1 = execute(program1)
    answer2 = execute(program2)
    return answer1 == answer2

def display(answer):
    if len(answer) > 5:
        print(answer[:5] + ["....."])
    else:
        print(answer)

def interactive_compare(program1, program2):
    answer1 = execute(program1)
    answer2 = execute(program2)
    display(answer1)
    display(answer2)
    print("Same denotation :", answer1 == answer2)
    return answer1 == answer2

if __name__ == "__main__":
    print("Interactive mode. Input program:")
    program = ""
    while 1:
        program1 = input()
        if program1 == "exit":
            break
        program2 = input()
        print("Running executor ...")
        interactive_compare(program1, program2)