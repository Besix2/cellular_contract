from flask import Flask, render_template, request, redirect, url_for 
from livereload import Server
import sys


sys.path.insert(0, "C:\\Users\\Myuse\\Downloads\\cellular_contract-main (1)\\cellular_contract-main")
print()
app = Flask(__name__)

@app.route('/')
def Home():
    return render_template("home.html")

class datastore():
    phone_name = None
    monthly_price = None
    deal_link = None
@app.route("/result_page")
def result_page():
    return render_template("result_page.html", phone_name=datastore.phone_name, monthly_price=datastore.monthly_price, deal_link=datastore.deal_link)

@app.route("/submit", methods=["POST"])
def submit():

    if request.method == "POST":
        text_value = float(request.form.get("options"))
        from compare import main
        result = main(text_value)
        datastore.monthly_price = result[0]
        datastore.phone_name = result[1]
        datastore.deal_link = result[2]
        return redirect(url_for("result_page"))


    
    

if __name__ == '__main__':
    app.run(debug=True)
