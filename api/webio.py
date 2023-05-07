#import all the required modules
from flask import Flask
from pywebio.platform.flask import webio_view
#from pywebio import STATIC_PATH 
from pywebio.input import*
from pywebio.output import*
from pywebio import start_server,config
import time
import os
import random as r
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
#connection to the database
db_url =os.getenv("MONGO_URI")
client = MongoClient(db_url)
db = client.school
sd = db.students

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

#custom css styling for our buttons
css = """
#pywebio-scope-background button{
    width:40%;
    height:10%;
    position:relative; 
    left:32%;
}
"""
config(theme='dark')
@config(css_style=css)
def main():
    #configure the theme and styling to our buttons 
    def bground():
        put_scope("background").style('''padding-top:5px;padding-bottom:5%; 
            border-radius:20px; background: rgb(84,121,128);background: 
            linear-gradient(0deg, rgba(84,121,128,1) 32%, rgba(45,150,152,1) 49%, rgba(153,153,153,1) 69%, rgba(47,149,153,1) 89%);
            ''')
        with use_scope("background"):
            #app Title Header
            put_html("<br/>")
            put_html("<h1> WELCOME TO <br/> The Ultimate Student Management System </h1>").style('''text-align:center;font-weight:650px; 
            font-style:bold;font-size:40px;color:#ffffff;text-shadow: 1.5px 1.5px #ff0000;''')

            #create a scope for general display of data from the management system
            put_scope("display").style('''background: rgb(58,168,189);
                background: linear-gradient(0deg, rgba(58,168,189,1) 16%, rgba(44,207,210,0.5242471988795518) 49%, rgba(153,153,153,0.6558998599439776) 69%, rgba(23,205,212,1) 95%);
                color:#0D2C4C;text-align:justify; padding:0.85em;position:relative;left:10%; margin:12px; border-radius:10px;
                width:80%;
                    ''')

            #create a scope for call to Action buttons
            with use_scope("CTA",clear=True):
                put_html("<br/><br/>")
                put_button("Enroll Student", onclick= lambda: studentEnroll())
                put_html("<br/><br/>")
                put_button("Student List", onclick= lambda: allStudents())
                put_html("<br/><br/>")
                put_button("Verify Identity", onclick= lambda: identity())
                put_html("<br/><br/>")
                put_button("Report", onclick= lambda: report())
                put_html("<br/><br/>")      
                    

                
    #create and configure the functions above to make our app fully functional
    def studentEnroll():
        #pass
        clear("display")
        idCode = r.randint(1000,1500)
        #input group for collecting all the required student data
        info = input_group('Add Student', [
        input('Name', type=TEXT, name='name', required=True, placeholder='Enter full Name'),
        input('Age', type=NUMBER, name = 'age', required=True, placeholder='Enter age (8-27)'),
        input('Class', type=TEXT, name='class', required=True, placeholder='Enter class e.g Grade 7'),
        input('Section', type=TEXT, name='section', required=True, placeholder='Enter Section e.g Science'),
        checkbox('Best subjects',['Physics','F.Maths','Biology','Hom Ec','Geography','Lit in English','ICT','Robotics'],
        inline=True, name='bestsdjects'),
        input('Role', type=TEXT, name='role', required=True, placeholder='Enter role or just write Student')],cancelable=True)

        
        #check if the submission is no void or empty:
        if info is not None:
            #This for the live server only
            put_warning("Invalid Request: You're not an Admin!",closable=True, scope="display").style("width:80%; margin:10%;")
            #create a query to of the student data to be inserted into database
            student = {
            'name':info['name'],
            'age':info['age'],
            'id':idCode,
            'class':info['class'],
            'section': info['section'],
            'role':info['role'],
            'bestsdjects':info['bestsdjects'],
            'records':[],
            'records_time':[],
            }
            #make an insertion into the database
            sd.insert_one(student)
            toast("%s  ID: %d  in Class: %s Added Successfully!"%(info['name'],idCode,info['class']),position='right', color='primary',duration=6)
        pos()


    def allStudents():
        #pass
        #this will query our database and list all the students according to names in descending order:
        clear("display")
        Tdata =[]
        for student in sd.find({}).sort('name', 1):
            name = student['name']
            Class = student['class']
            section = student['section']
            id = student['id']
            data = [name,section,Class,id]
            Tdata.append(data)
        #put the students list in a nice table with scrollable enabled
        put_scrollable(put_table(Tdata, header=['Name of Student','Section','Class','ID']), scope="display",border=False, height= 350).style("color:white;")
        pos()
                
                
    def identity():
        #pass
        clear("display")
        id = input_group('', [input('Student ID:', type=NUMBER,name="id", required=True, placeholder='Enter Student Unique ID')],cancelable=True)
        if id is not None:
            identity = sd.find_one({'id':id['id']})
            if identity is not None:
                #collect the identity of the student
                toast("ID: %d  Verified Successfully!"%(identity['id']),position='center', color='primary',duration=3)
                time.sleep(2)
                put_code("Name: %s  Class: %s  Age: %d "%(identity['name'],identity['class'], identity['age']), scope="display").style("text-align:center;")
            else:
                put_error("ID not Valid!",closable=True, scope="display").style("width:80%; margin:10%;")
        else:
            pass

        pos()


    def report():
        #pass
        clear("display")
        id = input_group('', [input('Student ID:', type=NUMBER,name="id", required=True, placeholder='Enter Student Unique ID')],cancelable=True)
        if id is not None:
            id = id['id']
            identity = sd.find_one({'id':id})

            if identity is not None:
                clear("CTA")
                with use_scope("background"):
                    put_html("<br/><br/>")
                    put_button("View Records", onclick= lambda x = id: records(x) )
                    put_html("<br/><br/>")
                    put_button("Add Report", onclick= lambda x= id: addReport(x) )
                    put_html("<br/><br/>")
                    put_button("<<Back", onclick= lambda:Home() )
                    put_html("<br/><br/>")
            else:
                put_error("ID not Valid!",closable=True, scope="display").style("width:80%; margin:10%;")
        else:
            pass
        pos()

    def records(id):
        #pass
        clear("display")
        query = sd.find_one({"id":id})
        records = query["records"]
        stamp = query['records_time']
        i = 0
        if len(records) !=0:
            for record in records:
                put_code((record + "   TimeStamp>" + stamp[i]), scope="display").style("text-align:center;")
                i += 1
        else:
            put_info("Student has no report in the database Records!",closable=True, scope="display").style("width:80%; margin:10%;") 
            
        pos()

    def addReport(id):
        #pass
        clear("display")
        report = input_group('',[input(placeholder="Enter a brief report", name ="report", required=True),], cancelable=True)
        timeStamp = time.strftime('%I:%M%p;%Y-%m-%d', time.localtime())
        #check in report is not empty
        if report is not None:
            #This for the live server only
            #put_warning("Invalid Request: You're not an Admin!",closable=True, scope="display").style("width:80%; margin:10%;")
            #update the student's records, and also add timestamp to records_time
            if sd.update_many({'id':id},{'$push':{'records':report["report"],'records_time':timeStamp}}):
                put_success("Report Added successfully!",closable=True, scope="display").style("width:80%; margin:10%;") 
            else:
                put_error("Error Occurred while adding Record, Try again!",closable=True, scope="display").style("width:80%; margin:10%;")    
        pos()

        
    def Home():
        #pass
        remove("background") #remove our background scope to avoid error
        bground() #add a fresh occurrence of background scope

    def pos():
        #this function returns and focuses on the display scope
        scroll_to("display", position='top')
    bground()

app.add_url_rule('/', 'webio_view', webio_view(main),methods=['GET','POST'])   

if __name__ == "__main__":
    #start_server(bground,debug=True)
    app.run(session_expire_seconds=1000,debug=False)
    
