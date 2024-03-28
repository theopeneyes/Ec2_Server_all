# from fastapi import FastAPI, Request, Form
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import mysql.connector
# import nltk
# import re
# import openai
# nltk.download('punkt')

# openai.api_key = "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"

# def semantic_analysis(objective,feedback):
#     try:
#         x=openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#                 {"role": "user", "content": "Find arbitrary semantic similarity in percentage between"+" "+objective+" "+'and'+" "+feedback+" please always generate percentage value"},                
#                 ],
#         temperature=0.0
#         )
#         result=x['choices'][0]['message']['content']
#         match = re.search(r"\b\d{1,3}(?:\.\d{1,3})?%?\b", result)  # search for the pattern in the feedback string
#         if match:
#             percentage = match.group()  # extract the matched percentage value       
#         else:
#             percentage=0
#         return int(percentage)
#     except :
#         return "Sorry, the server is currently unavailable. Please try again later."  

# # x=semantic_analysis(objective,feedback)
# # output=correlation_bw_obj_feedback(x)
# # output
# ##local mysql
# ###mysql -u root -p
# ####SET PASSWORD FOR 'myuser'@'localhost' = PASSWORD('1234');

# # mydb = mysql.connector.connect(
# #   host="localhost",
# #   user="myuser",
# #   password="1234",
# #   database="subjective_outcomes"
# # )

# ##server mysql
# mydb = mysql.connector.connect(
#   host="prodbyopeneyes.com",
#   user="prodbyopeneyes_subjective-outcomes",
#   password="euWfr.}i%FN2",
#   database="prodbyopeneyes_subjective-outcomes"
# )

# mycursor = mydb.cursor()

# templates = Jinja2Templates(directory="templates/")

# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # if app.debug:
# #     print("Debug mode is on")
# # else:
# #     print("Debug mode is off")

# @app.get("/")
# def form_post(request: Request):
#     return templates.TemplateResponse('login.html', context={'request': request, 'result_single_text' : '','result_single': '', 'result_multi': '', 'feedback': '', 'objective': ''}, status_code=200)

# @app.post("/get-data")
# async def get_data(request: Request, pinNumber: int = Form(...)):
#     mycursor.execute("SELECT pin FROM login WHERE pin = %s", (pinNumber,))
#     result = mycursor.fetchall()
#     return result

# @app.get("/resp")
# def form_post(request: Request):
#     return templates.TemplateResponse('form.html', context={'request': request}, status_code=200)

# def insert_data(pin,objective, feedback,result_multi):
#     mycursor = mydb.cursor()
#     sql = "INSERT INTO oai_outcomes (pin, objective, feedback, oai_feedback) VALUES (%s, %s, %s, %s)"
#     val = (pin, objective, feedback, result_multi)
#     print(val)
#     mycursor.execute(sql, val)
#     mydb.commit()

# @app.post('/derived_relevance/{name}')
# def form_post(request: Request,name: str, objective: str = Form(...), feedback: str = Form(...)):
#         if(objective != '' and feedback != ''):
#             multi_percent_is = semantic_analysis(objective, feedback)
#             result_multi = multi_percent_is
#             insert_data(name ,objective, feedback,result_multi)
#             return templates.TemplateResponse('form.html', context={'request': request, 'result_multi': result_multi, 'feedback': feedback, 'objective': objective}, status_code=200)
#         else:
#             return templates.TemplateResponse('form.html', context={'request': request, 'result_multi': '', 'feedback': feedback, 'objective': objective}, status_code=200)

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sentence_transformers import SentenceTransformer, util
from nltk import sent_tokenize
import mysql.connector
import nltk
import re
nltk.download('punkt')

# local mysql
# mysql -u root -p
# SET PASSWORD FOR 'myuser'@'localhost' = PASSWORD('1234');

# mydb = mysql.connector.connect(
#     host="localhost",
#     user="myuser",
#     password="1234",
#     database="subjective_outcomes"
# )

# server mysql
mydb = mysql.connector.connect(
  host="prodbyopeneyes.com",
  user="prodbyopeneyes_subjective-outcomes",
  password="euWfr.}i%FN2",
  database="prodbyopeneyes_subjective-outcomes"
)

mycursor = mydb.cursor()
# model = SentenceTransformer('BAAI/bge-large-zh')
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
templates = Jinja2Templates(directory="templates/")


def clean_sentence(sentence):
    sentence = sentence.strip()
    sentence = re.sub(r'^[\d#\*@]+[\.\)]*\s*', '', sentence)
    sentence = sentence.replace('•', '')
    sentence = sentence.strip()
    return sentence


def multi_sentence_similarity(text: str, user_input: str):
    text = clean_sentence(text)
    user_input = clean_sentence(user_input)
    sentences = [text, user_input]
    embedding_1 = model.encode(sentences[0], convert_to_tensor=True)
    embedding_2 = model.encode(sentences[1], convert_to_tensor=True)
    tensor_value = util.pytorch_cos_sim(embedding_1, embedding_2)
    percentage = tensor_value.item()
    percent = "{:.2%}".format(percentage)
    return percent


def single_sentence_similarity(text: str, user_input: str):
    text = clean_sentence(text)
    input = sent_tokenize(user_input)
    embedding_1 = model.encode(text, convert_to_tensor=True)
    max_score = -1
    max_sentence = ""
    for sentence in input:
        sentence = clean_sentence(sentence)
        embedding_2 = model.encode(sentence, convert_to_tensor=True)
        tensor_value = util.pytorch_cos_sim(embedding_1, embedding_2)
        score = tensor_value.item()
        if score > max_score:
            max_score = score
            max_sentence = sentence
    percent = "{:.2%}".format(max_score)
    return (percent, max_sentence)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def form_post(request: Request):
    return templates.TemplateResponse('login.html', context={'request': request, 'result_single_text': '', 'result_single': '', 'result_multi': '', 'feedback': '', 'objective': ''}, status_code=200)


@app.post("/get-data")
async def get_data(request: Request, pinNumber: int = Form(...)):
    mycursor.execute("SELECT pin FROM login WHERE pin = %s", (pinNumber,))
    result = mycursor.fetchall()
    return result


@app.get("/home")
def form_post(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request}, status_code=200)


def insert_data(pin,objective,feedback,entire_feedback,specific_feedback):
    mycursor = mydb.cursor()
    sql = "INSERT INTO outcomes (pin,objective,feedback,entire_feedback,specific_feedback) VALUES (%s,%s,%s,%s,%s)"
    val = (pin,objective,feedback,entire_feedback,specific_feedback)
    print(val)
    mycursor.execute(sql,val)
    mydb.commit()


@app.post('/derived_relevance/{name}')
def form_post(request: Request, name: str, objective: str = Form(...), feedback: str = Form(...)):
    if(objective != '' and feedback != ''):
        multi_percent_is = multi_sentence_similarity(objective, feedback)
        single_percent_is = single_sentence_similarity(objective, feedback)
        result_single_per = single_percent_is[0] + " :"
        result_single_per_without_percent_sign_sing = result_single_per.replace(
            "%", "").replace(":", "")
        result_single_text = '"'+single_percent_is[1]+'"'
        result_multi = ": " + multi_percent_is + "."
        result_single_per_without_percent_sign_mult = multi_percent_is.replace(
            "%", "").replace(":", "")
        insert_data(name, objective, feedback, result_single_per_without_percent_sign_mult,
                    result_single_per_without_percent_sign_sing)

        return templates.TemplateResponse('form.html', context={'request': request, 'result_single_text': result_single_text, 'result_single_per': result_single_per, 'result_multi': result_multi, 'feedback': feedback, 'objective': objective}, status_code=200)
    else:
        return templates.TemplateResponse('form.html', context={'request': request, 'result_single_text': result_single_text, 'result_single_per': result_single_per, 'result_multi': '', 'feedback': feedback, 'objective': objective}, status_code=200)
