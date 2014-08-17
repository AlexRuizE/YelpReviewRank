#! /usr/bin/python3.4

from flask import Flask, render_template, request
from flask.json import jsonify
from app import app
import pymysql as mdb

db = mdb.connect(user="root", passwd='macmac', host="localhost", db="world_innodb", charset='utf8')
 
import numpy, pandas, random, urllib.request


#Define functions
def get_random_user():
    uid=random.sample(users, 1)
    return uid


def get_random_business():
    bid1=list()
    bid1+=random.sample(business, 1)
    bid1.append(yelp['name.business'][yelp['business_id']==bid1[0]].unique()[0])
    return bid1[0]


def get_business_id(restaurant):
    bid=yelp['business_id'][yelp['name.business']==restaurant]
    bid=bid.unique()[0]
    return bid


def predict_expected_value(x1, x2, x3, x4, x5):
    beta_hat=[0.677822, 0.058382, -0.006086, -0.145137, 0.002315, -0.067844]
    x_i=[1, x1, x2, x3, x4, x5]
    y_hat=numpy.dot(beta_hat, x_i)
    return y_hat


def get_highest_reviews(bid):
    other_reviewers_of_restaurant=list(yelp['user_id'][yelp['business_id']==bid])
    uid=random.sample(other_reviewers_of_restaurant, 1)
    user_column=pandas.match(uid, users)[0]
    similarity_indices_for_user=list(df.ix[:,user_column])
    z=numpy.array(similarity_indices_for_user)
    most_similar_users=numpy.argsort(z)[0:10]
    most_similar_users=[users[most_similar_users[i]] for i in range(10)]
    name_rest=yelp['name.business'][yelp['business_id']==bid].unique()[0]
    f =  lambda row: row['user_id'] in most_similar_users and row['name.business'] in name_rest
    k = yelp.apply(f, axis=1)
    temp=yelp[k]
    temp.iloc[:,[1,3,6,9,11,17,21,27]]
    x1=list(temp['stars.review']); x2=list(temp['richness']); x3=list(temp['fans'])
    x4=list(temp['review_count.review']); x5=list(temp['stars.business'])
    predicted_values=list()   
    for i in range(len(temp)):
        predicted_values.append(predict_expected_value(x1[i],x2[i],x3[i],x4[i],x5[i]))
    highest_review=predicted_values.index(max(predicted_values))
    return temp['text'].iloc[highest_review]

def get_highest_reviews(bid):
    other_reviewers_of_restaurant=list(yelp['user_id'][yelp['business_id']==bid])
    uid=random.sample(other_reviewers_of_restaurant, 1)
    user_column=pandas.match(uid, users)[0]
    similarity_indices_for_user=list(df.ix[:,user_column])
    z=numpy.array(similarity_indices_for_user)
    most_similar_users=numpy.argsort(z)[0:10]
    most_similar_users=[users[most_similar_users[i]] for i in range(10)]
    name_rest=yelp['name.business'][yelp['business_id']==bid].unique()[0]
    f =  lambda row: row['user_id'] in most_similar_users and row['name.business'] in name_rest
    k = yelp.apply(f, axis=1)
    temp=yelp[k]
    temp.iloc[:,[1,3,6,9,11,17,21,27]]
    x1=list(temp['stars.review']); x2=list(temp['richness']); x3=list(temp['fans'])
    x4=list(temp['review_count.review']); x5=list(temp['stars.business'])
    predicted_values=list()
    for i in range(len(temp)):
        predicted_values.append([predict_expected_value(x1[i],x2[i],x3[i],x4[i],x5[i]), i])
    predicted_values.sort(key=lambda x: x[0])
    predicted_values=predicted_values[-3:]
    predicted_values.sort(key=lambda x: x[1])
    reviews=list()
    for value in range(len(predicted_values)):
        row_of_review=predicted_values[value][1]
        print(row_of_review)
        reviews.append(temp['text'].iloc[row_of_review])
    return reviews


# Yelp dataset (reduced)
yelp=pandas.read_csv('/home/monorhesus/Documents/Insight/Project/yelp.website.csv')

# Matrix of euclidean distances
df=pandas.read_csv('/home/monorhesus/Documents/Insight/Project/euc.distance.website.csv')
users_euc=list(df.columns)

# List of ordered users
users=pandas.read_csv('/home/monorhesus/Documents/Insight/Project/euc.distance.websiteUSERS.csv')
users=list(users.values.ravel())

# List of ordered businesses
business=pandas.read_csv('/home/monorhesus/Documents/Insight/Project/business_id.csv')
business=list(business.values.ravel())
restaurants=list(yelp['name.business'].unique())


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home', user = { 'nickname': 'Miguel' },
        )

@app.route("/jquery")
def index_jquery():
	return render_template('index_js.html')

@app.route("/yelp")
def yelp_query():
	return render_template('index_js.html')

@app.route('/db')
def cities_page():
    with db: 
        cur = db.cursor()
        cur.execute("SELECT Name FROM City LIMIT 15;")
        query_results = cur.fetchall()
    cities = ""
    for result in query_results:
        cities += result[0]
        cities += "<br>"
    return cities


@app.route("/db_fancy")
def cities_page_fancy():
	with db:
		cur = db.cursor()
		cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")

		query_results = cur.fetchall()
	cities = []
	for result in query_results:
		cities.append(dict(name=result[0], country=result[1], population=result[2]))
	return render_template('cities.html', cities=cities)


@app.route("/db_json")
def cities_json():
	with db:
		cur = db.cursor()
		cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population;")

		query_results = cur.fetchall()
	cities = []
	for result in query_results:
		cities.append(dict(name=result[0], country=result[1], population=result[2]))
	return jsonify(dict(cities=cities))



@app.route("/review", methods=['GET'])
def index_review():
	restaurant = request.args.get('restaurant')
	bid = get_business_id(restaurant)
	reviews=get_highest_reviews(bid)
	return render_template('review.html', reviews=reviews)



