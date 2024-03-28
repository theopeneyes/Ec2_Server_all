from mcq_generation import mcq
from boolean_generation import Boolean_question
from descriptive_generation import descriptive_questions
from fib_mcq_generation import fib_with_mcq #fib-fibmcq 
from multiple_boolean_generation import boolean_multiple_statement  #mcb-bb
import json
import itertools

def flatten(list_of_lists):
        return list(itertools.chain.from_iterable(list_of_lists))

def error_handler(ques_list,type_of_question):
    error_ques_list = []
    type_of_questions = [item['question_type'] for item in type_of_question ]
    for i, question_type in enumerate(type_of_questions):
        if not ques_list[i]:
            # ques_list[i].append({'error': f'Not able to generate {question_type} type questions'})
            error_ques_list.append({'error': f'Not able to generate {question_type} type questions'})
    return ques_list,error_ques_list

# Flatten the list of lists, convert each dictionary to a JSON string, and then remove duplicates
def remove_duplicate(ques_list):
    flat_questions = [item for sublist in ques_list for item in sublist]
    json_strings = [json.dumps(d, sort_keys=True) for d in flat_questions]
    unique_json_strings = set(json_strings)
    recommended_questions = [json.loads(s) for s in unique_json_strings]
    return recommended_questions


def getAllGeneratedQuestions(Text, type_of_question,file_type): 
    recommended_questions=[]
    additional_questions=[]
    for i in type_of_question:
        if i["question_type"] == "bool_statement":
            boolean_statement=boolean_multiple_statement(Text,"bool_statement",file_type)
            # if len(boolean_statement) == 0:
            #     boolean_statement = [{"message":"Not able to generate bool_statement"}]
            # else:
            req_ques=i["no_of_que"]
            recommended_questions.append(boolean_statement[:req_ques])
            additional_questions.append(boolean_statement[req_ques:])
        elif i["question_type"] == "boolean":
            boolean_questions=Boolean_question(Text,file_type)
            req_ques=i["no_of_que"]
            recommended_questions.append(boolean_questions[:req_ques])
            additional_questions.append(boolean_questions[req_ques:])
        elif i["question_type"] == "mcq":
            mcq_questions=mcq(Text,file_type)
            req_ques=i["no_of_que"]
            recommended_questions.append(mcq_questions[:req_ques])
            additional_questions.append(mcq_questions[req_ques:])
        elif i["question_type"] == "wh":
            des_ques=descriptive_questions(Text,file_type)
            req_ques=i["no_of_que"]
            recommended_questions.append(des_ques[:req_ques])
            additional_questions.append(des_ques[req_ques:])
        elif i["question_type"] == "mcq_fib":
            fib_mcq=fib_with_mcq(Text,"mcq_fib",file_type)
            req_ques=i["no_of_que"]
            recommended_questions.append(fib_mcq[:req_ques])
            additional_questions.append(fib_mcq[req_ques:])
        elif i["question_type"] == "bool_fib":
            # bool_fib=boolean_single_statement(final)
            bool_fib=boolean_multiple_statement(Text,"bool_fib",file_type)
            req_ques=i["no_of_que"]
            recommended_questions.append(bool_fib[:req_ques])
            additional_questions.append(bool_fib[req_ques:])
        elif i["question_type"] == "fib":
            fib_only=fib_with_mcq(Text,"fib",file_type)
            req_ques=i["no_of_que"]
            recommended_questions.append(fib_only[:req_ques])
            additional_questions.append(fib_only[req_ques:])

    # def convert_lists_to_tuples(d):
    #     return tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in d.items())
    # additional_questions_ = [dict(t) for t in {convert_lists_to_tuples(d) for d in flatten(additional_questions)}]
    # recommended_questions_ = [dict(t) for t in {convert_lists_to_tuples(d) for d in flatten(recommended_questions)}]
    recommended_questions_ = error_handler(recommended_questions,type_of_question)[0]
    additional_questions_ = error_handler(additional_questions,type_of_question)[0]
    error_ques_list = error_handler(recommended_questions_,type_of_question)[1]
    recommended_questions = remove_duplicate(recommended_questions_)
    additional_questions = remove_duplicate(additional_questions_)
    return recommended_questions,additional_questions,error_ques_list

    


# Error message for blank list


