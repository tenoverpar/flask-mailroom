import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from peewee import fn
from model import Donor, Donation

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('all'))


@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/report/')
def report():
    donations = Donation.select(Donation.donor, fn.Sum(Donation.value).alias
                                ('total'), fn.Avg(Donation.value).alias
                                ('average')).group_by(Donation.donor)
    return render_template('report.jinja2', donations=donations)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        donor, created = Donor.get_or_create(name=request.form['name'])
        donation = Donation(value=request.form['donation'], donor=donor)
        donation.save()

        return redirect(url_for('all'))
    else:
        return render_template('create.jinja2')


@app.route('/genemail/', methods=['GET', 'POST'])
def genemail():
    if request.method == 'POST':
        donor = Donor.get_or_none(Donor.name == request.form['name'])

        if donor is not None:
            return redirect(url_for('viewemail', donor=donor.name))
        else:
            return render_template('genemail.jinja2',
                                   error="That donor does not exist.")
    else:
        return render_template('genemail.jinja2')


@app.route('/viewemail/<donor>')
def viewemail(donor):
    total = 0
    count = 0
    donations = Donation.select().join(Donor).where(Donor.name == donor)
    for donation in donations:
        total += donation.value
        count += 1
    return render_template('viewemail.jinja2', donor=donor, total=total,
                           count=count)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
app.run(host='0.0.0.0', port=port)
