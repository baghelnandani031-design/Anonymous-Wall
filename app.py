from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime # यह लाइन सबसे ऊपर जोड़ें

import os

app = Flask(__name__)

# 1. Database Configuration (SQLite का उपयोग)
# यह आपके प्रोजेक्ट फोल्डर में 'database.db' नाम की फाइल बना देगा
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Compliment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    # यह लाइन जोड़ना भूल गए थे:
    date_posted = db.Column(db.DateTime, default=datetime.utcnow) 

    def __repr__(self):
        return f'<Compliment {self.id}>'
# पहली बार डेटाबेस टेबल बनाने के लिए (Python shell की ज़रूरत नहीं पड़ेगी)
with app.app_context():
    db.create_all()

# 3. Routes
@app.route('/')
def index():
    # डेटाबेस से सभी मैसेज निकालें (ताकि वॉल पर दिखें)
    all_messages = Compliment.query.order_by(Compliment.id.desc()).all()
    return render_template('index.html', messages=all_messages)

@app.route('/post', methods=['POST'])
def post_message():
    msg_content = request.form.get('compliment_text')
    
    if msg_content:
        # नया मैसेज डेटाबेस में जोड़ें
        new_compliment = Compliment(text=msg_content)
        db.session.add(new_compliment)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    # सावधानी: यह डेटाबेस के सभी मैसेज डिलीट कर देगा
    Compliment.query.delete()
    db.session.commit()
    return redirect(url_for('index'))
# Admin Dashboard Route
@app.route('/dashboard')
def dashboard():
    # डेटाबेस से सभी मैसेज निकालें
    all_messages = Compliment.query.order_by(Compliment.date_posted.desc()).all()
    # मैसेज की कुल गिनती (Total Count)
    total_count = Compliment.query.count()
    return render_template('dashboard.html', messages=all_messages, count=total_count)

# . डिलीट रूट (Specific Message Delete)
@app.route('/delete/<int:id>')
def delete_message(id):
    msg_to_delete = Compliment.query.get_or_404(id)
    db.session.delete(msg_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)