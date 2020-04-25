from flask import Flask, escape, request
import sqlite3
import math 
import json
import ast 
import sys

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False 

conn = sqlite3.connect('273hw2.db')

c = conn.cursor()

c.execute('''CREATE TABLE if NOT EXISTS tests 
             (test_id INTEGER PRIMARY KEY, subject TEXT, answer_keys BLOB)''')

c.execute('''CREATE TABLE submissions
             (scantron_id INTEGER, testId REFERENCES tests(test_id), scantron_url TEXT, name TEXT, subject TEXT, score INTEGER, result TEXT)''')

c

conn.commit()

conn.close()


tid = 1

sid = 1


#home 

@app.route('/api')

def hello():
    
  return f'CMPE273-Assignment2!'



#create test

@app.route('/api/tests',methods=['POST'])

def create_tests():
      
   global tid
  
   subject = request.json["subject"]

   answer_keys = request.json["answer_keys"]

   conn = sqlite3.connect('273hw2.db')

   c = conn.cursor()
   
   c.execute("INSERT INTO tests VALUES (?,?,?)",[tid, subject, str(answer_keys)])

   conn.commit()

   res = "\n" + "201 Created" + "\n" + "\n" + "{" + "\n" + "\n" + "test_id:"+str(tid) + "\n" + "\n" + "subject:"+str(subject) + "\n" + "\n" +"answer_keys:"+"\n"+str(answer_keys) + "\n" + "\n" + "submissions:[]" + "\n"+ "\n" + "}" 

   tid += 1

   conn.close()

   

   return res
 
  
#retrieve specific test

@app.route('/api/tests/<t_id>',methods=['GET'])

def retrieve_test(t_id):
      
 conn = sqlite3.connect('273hw2.db')

 c = conn.cursor()

 c.execute("SELECT * FROM tests WHERE test_id = ? ",str(t_id))

 test = c.fetchone()

 c.execute("SELECT * FROM submissions WHERE testId = ?",str(t_id))

 re = c.fetchall()

 submissions = []

 for i in re:
       
       submissions.append({

    "scantron_id": i[0],
    "scantron_url": i[2],
    "name": i[3],
    "subject": i[4],
    "score": i[5],
    "result": ast.literal_eval(i[6])

         

       })

 r = test[2]

 answer_keys = ast.literal_eval(r)

 res = "\n" + "{" + "\n" + "\n" + "test_id:"+str(test[0]) + "\n" + "\n" + "subject:"+str(test[1]) + "\n" + "\n" +"answer_keys:"+ "\n"+str(answer_keys) + "\n" + "\n" + "submissions:" + "\n" + str(submissions) + "\n"+ "\n" + "}" 

 conn.close()

 return res
 


#submit scantron and add it to a test 

@app.route('/api/tests/<t_id>/scantrons',methods=['POST'])

def add_scantron_to_test(t_id):
      
   score = 0

   global sid
   
   f = request.files['data']

   file = f.read()

   scantron = json.loads(file)
   
   scantron_url = "http://localhost:5000/files/scantron-"+ str(sid)+".json"

   name = scantron["name"]

   subject = scantron["subject"]

   answers = scantron["answers"]

   invalid = []

   for i in range(1,len(answers)+1):
      
    if (answers[str(i)] not in ["A","B","C","D"]):

     invalid.append(str(i))

   inv = ("invalid answer at question" + str(invalid))
         
   conn = sqlite3.connect('273hw2.db')

   c = conn.cursor()

   c.execute("SELECT * FROM tests WHERE test_id = ? ", str(t_id))

   r = c.fetchone()

   re = r[2]

   answer_keys = ast.literal_eval(re)

   result = {}

   for i in range(1,len(answer_keys)+1):
          
      if (answers[str(i)] == answer_keys[str(i)]):
             
             score = score + 2 

      result.update({
       str(i):{
               "actual":answers[str(i)],

               "expected":answer_keys[str(i)]
               }
               })

   res = "\n" + "201 Created" + "\n" + "\n" + str(inv) +"\n" + "\n" + "{" + "\n" + "\n" + "scantron_id:"+str(sid) + "\n" + "\n" + "scantron_url:"+str(scantron_url) + "\n" + "\n" +"name:"+str(name) + "\n" + "\n" + "subject:" + str(subject) + "\n"+ "\n" + "score:" + str(score) + "\n" + "\n" + "result:" + "\n"+str(result)+ "\n" + "\n" + "}" 

   
   c.execute("INSERT INTO submissions(scantron_id, testId, scantron_url, name, subject, score, result) VALUES (?,?,?,?,?,?,?)",[sid,t_id,scantron_url, name, subject, score, str(result)])
   
   conn.commit()

   conn.close()

   sid += 1
       
   return res

   
  

  
   
@app.route('/files/<file_name>',methods=['GET'])



def get_scantron(file_name):
      
 conn = sqlite3.connect('273hw2.db')
 
 c = conn.cursor()

 url = "http://localhost:5000/files/" + file_name

 c.execute("SELECT * FROM submissions WHERE scantron_url = ?",[url])

 scantron = c.fetchone()

 res = "\n" + "{" + "\n" + "\n" + "scantron_id:"+str(scantron[0]) + "\n" + "\n" +"name:"+str(scantron[3]) + "\n" + "\n" + "subject:" + str(scantron[4]) + "\n"+ "\n" + "score:" + str(scantron[5]) + "\n" + "\n" + "result:" +"\n"+ str(scantron[6])+ "\n" + "\n" + "}" 

 
 conn.close()

 return res


             
     
     

   










      




  
 


 
  











