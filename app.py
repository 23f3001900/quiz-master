from flask import Flask,render_template

app= Flask(__name__)

import config
import models

import routes

if __name__=='__main__': #check to see if the script is directly run or it is being imported by someone else
    app.run(debug=True)