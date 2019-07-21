import flask 
from stopwords import stopwords
from bs4 import BeautifulSoup
from markdown import markdown
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

@app.route('/search',methods=['GET', 'POST'])
def searchquery():
    content = request.json
    data = content["query"]
    badChar = [";","-","/",":","<",">","?"]
    for dat in badChar:
        data.replace(dat,"")
    querybeg = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=relevance&q="
    queryend = "&filter=withbody&site=stackoverflow"
    r = requests.get(querybeg + data + queryend)
    val = r.json()
    relate =[]
    answ = []
    questions = []
    items = val["items"]
    qtags = []
    j = 0
    print(data, len(items))
    for item in items:
        if(j<3):
            time.sleep(0.2)
            qId = item["question_id"]
            qLink = item["link"]
            uname = item["owner"]["display_name"]
            profimage = item["owner"]["profile_image"]
            qtitle = item["title"]
            if(len(qtags)<1):
                qtags = item["tags"]
            qtitle = ''.join(BeautifulSoup(qtitle, features="html5lib").findAll(text=True))
            qtitle = qtitle.replace("&#39;","'")
            qtitle = qtitle.replace("&lt;","<")
            qtitle = qtitle.replace("&gt;",">")
            qhtml = item["body"]
            qbody = ''.join(BeautifulSoup(qhtml, features="html5lib").findAll(text=True))
            qbody = qbody.replace("&quot;","'")
            qbody = qbody.replace("&lt;","<")
            qbody = qbody.replace("&gt;",">")
            qscore = item["score"]
            answered = item["is_answered"]
            print(type(answered))
            if(len(relate) <10):
                relQuesBeg = "http://api.stackexchange.com/questions/"
                relQuesEnd = "/linked?order=desc&sort=activity&site=stackoverflow"
                relQues  = relQuesBeg + str(qId) + relQuesEnd
                related = requests.get(relQues)
                related = related.json()
                relatedItems = related["items"]
                relatedItems = relatedItems[0:4]
                for ri in relatedItems:
                    link = ri["link"]
                    title = ri["title"]
                    obj = {"link": link , "title": title}
                    if obj not in relate:
                        relate.append(obj)

        
            if(answered):
                answersBeg = "http://api.stackexchange.com/2.2/questions/"
                answersEnd = "/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody"
                answers = answersBeg + str(qId) + answersEnd
                ans = requests.get(answers)
                ans = ans.json()
                ansItems = ans["items"]
                ansIt = []
                i = 0
                for ai in ansItems:
                    if(i<2):
                        score = ai["score"]
                        reputation = ai["owner"]["reputation"]
                        name = ai["owner"]["display_name"]
                        link = qLink + "#answer-" + str(ai["answer_id"])
                        accepted = ai["is_accepted"]
                        html = ai["body"]
                        body = ''.join(BeautifulSoup(html, features="html5lib").findAll(text=True))
                        body = body.replace("&quot;","'")
                        body = body.replace("&lt;","<")
                        body = body.replace("&gt;",">")
                        profile_image =ai["owner"]["profile_image"]
                        obj = {"score":score, "accepted":accepted , "body":body , "reputation":reputation , "image":profile_image , "name":name, "link":link , "question": qtitle}
                        answ.append(obj)
                    i += 1
            

            quesobj = {
                "id": qId,
                "link": qLink,
                "username": uname,
                "image": profimage,
                "title": qtitle,
                "body": qbody,
                "score":qscore
            }

            questions.append(quesobj)
        j+=1

    retobj = {"questions": questions , "related": relate , "answers": answ , "tags":qtags}

    return jsonify(retobj)


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 12345 # If you don't provide any port the port will be set to 12345



    app.run(port=port)