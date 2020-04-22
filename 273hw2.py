from flask import Flask, escape, request
import sqlite3
import math 
import json
import ast 

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False 

conn = sqlite3.connect('273hw2.db')

c = conn.cursor()

c.execute('''CREATE TABLE if NOT EXISTS tests 
             (test_id INTEGER PRIMARY KEY, subject TEXT, answer_keys BLOB)''')

c.execute('''CREATE TABLE submissions
             (scantron_id INTEGER, testId REFERENCES tests(test_id), scantron_url TEXT, name TEXT, subject TEXT, score INTEGER, result TEXT)''')

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

   res = {
     "test_id":tid,
     "subject":subject,
     "answer_keys":answer_keys,
     "submissions":[]
     
     }

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

 res = {
   "test_id":test[0],
   "subject":test[1],
   "answer_keys":answer_keys,
   "submissions": submissions
 }

 conn.close()

 return res
 


#submit scantron and add it to a test 

@app.route('/api/tests/<t_id>/scantrons',methods=['POST'])

def add_scantron_to_test(t_id):
      
   score = 0

   global sid

   scantron_url = request.json["scantron_url"]
   
   name = request.json["name"]

   subject = request.json["subject"]

   my_answer = request.json["my_answer"]

   conn = sqlite3.connect('273hw2.db')

   c = conn.cursor()

   c.execute("SELECT * FROM tests WHERE test_id = ? ", str(t_id))

   r = c.fetchone()

   re = r[2]

   answer_keys = ast.literal_eval(re)

   result = {}

   for i in range(1,len(answer_keys)+1):
          
      if (my_answer[str(i)] == answer_keys[str(i)]):
             
             score = score + 2 

      result.update({
       str(i):{
               "actual":my_answer[str(i)],

               "expected":answer_keys[str(i)]
               }
               })

   res = {
    "scantron_id": sid,
    "scantron_url": scantron_url,
    "name": name,
    "subject": subject,
    "score": score,
    "result": result
    }
   
   c.execute("INSERT INTO submissions(scantron_id, testId, scantron_url, name, subject, score, result) VALUES (?,?,?,?,?,?,?)",[sid,t_id,scantron_url, name, subject, score, str(result)])
   
   conn.commit()

   conn.close()

   sid += 1
       
   return res

  
   
             
     
     

   










      




  
 


 
  











