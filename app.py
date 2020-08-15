from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from random import randint
import string
import os


def parseConfig():
    config_dict = {}
    file = open('config.txt','r')
    for line in file:
        line = line.replace("=", " ")
        kv = line.split()
        key = kv[0]
        value = kv[1]
        config_dict[key] = value
    return config_dict

# for config when running in local computer to keep credentials safe
config_dict = parseConfig()
user = config_dict["user"]
host = config_dict["host"]
password = config_dict["password"]
port = config_dict["port"]
database = config_dict["database"]

app = Flask(__name__)
sql_db_uri = 'mysql://'+ user + ':' + password + '@' + host + ':' + port + '/' + database
app.config['SQLALCHEMY_DATABASE_URI'] = sql_db_uri
db = SQLAlchemy(app)


# Models
Portfolio = db.Table('portfolio',
            db.Column('influencer_id', db.Integer,db.ForeignKey('influencer.influencer_id')),
            db.Column('sponsor_id', db.Integer, db.ForeignKey('sponsor.sponsor_id')))


class Influencer(db.Model):
    influencer_id = db.Column(db.Integer,primary_key=True)
    fullname = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    followers = db.Column(db.Integer)
    profile_picture = db.Column(db.LargeBinary)
    active_location = db.Column(db.String(100))

    influencers_relationship = db.relationship('Sponsor', secondary=Portfolio, backref=db.backref('influencers', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.username

class Sponsor(db.Model):
    sponsor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    active_location = db.Column(db.String(100))

    def __repr__(self):
        return '<Sponsor %r>' % self.name




# Routes


# Sponsor routes
@app.route('/addsponsor', methods=['POST'])
def add_sponsor():
    if request.is_json:
        data = request.get_json()
        print(data)
        sponsor_object = parseSponsor(data)
        if sponsor_object is not None:
            try:
                db.session.add(sponsor_object)
                db.session.commit()
            except Exception as e:
                return (str(e),400)
            return data
        else:
            return ('Bad request',400)
    else:
        return ('Request must be json',400)

@app.route('/sponsor',methods=['GET'])
def get_sponsor_info_from_id():
    sponsor_id = request.args.get('sponsor_id')
    if sponsor_id is not None:
        sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
        if sponsor is not None:
            sponsor_dict = sponsor.__dict__
            del sponsor_dict["_sa_instance_state"]
            return (sponsor_dict,200)
        else:
            return ('User not found')
    else:
        return ('Bad Request',400)


# Influencers routes

# #/getinvites?username={username}
# @app.route('/getinvites',methods=['GET'])
# def get_invites():
#     username = request.args.get('username')
#
#     if username is not None:
#         influencer = Influencer.query.filter_by(username=username).first()
#         sponsor_lists = influencer.influencers_relationship
#         for sponsor in sponsor_lists:
#             sponsor
#
#     else:
#         return ('username param empty')


@app.route('/addinfluencer',methods=['POST'])
def add_influencer():
    if request.is_json:
        data = request.get_json()
        influencer_object = parseInfluencer(data)
        if influencer_object is not None:
            try:
                db.session.add(influencer_object)
                db.session.commit()
            except Exception as e:
                return (str(e),400)
            return data
        else:
            return ('Bad request',400)
    else:
        return ('Request must be json',400)


# /influencer?username={username}
@app.route('/influencer', methods=['GET'])
def get_influencer_info_from_username():
    username = request.args.get('username')
    print(username)
    if username is not None:
        influencer = Influencer.query.filter_by(username=username).first()
        if influencer is not None:
            influencer_dict = influencer.__dict__
            del influencer_dict["_sa_instance_state"]
            return (influencer_dict,200)
        else:
            return ('User not found')
    else:
        return ('Bad Request',400)


# Portfolio, Invitation
@app.route('/inviteinfluencer', methods=['POST'])
def inviteInfluencer():
    # send sponsorid and #userid
    if request.is_json:
        data = request.get_json()
        invite = parseInvite(data)
        if invite is None:
            return ('Influencer or Sponsor does not exist', 400)
        else:
            sponsor = invite["sponsor"]
            influencer = invite["influencer"]
            sponsor.influencers.append(influencer)
            db.session.commit()
            return ("Invited")

    else:
        return ('Request must be JSON',400)




if __name__ == '__main__':
    app.run()

# parsers
def parseInvite(dict):
    sponsor_id = dict.get("sponsor_id")
    influencer_username = dict.get("username")

    if sponsor_id is None or influencer_username is None:
        return None
    else:
        # check if they exist
        sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
        influencer = Influencer.query.filter_by(username=influencer_username).first()
        if sponsor is None or influencer is None:
            return None
        else:
            return {"sponsor": sponsor , "influencer": influencer}

def parseSponsor(dict):
    sponsor_id = randint(1,2**31 - 1)
    name = dict.get("name")
    active_location = dict.get("active_location")

    if name == None:
        return None
    return Sponsor(sponsor_id=sponsor_id, name=name,active_location=active_location)

def parseInfluencer(dict):
    influencer_id = randint(1,2**31 - 1)
    fullname = dict.get("fullname")
    username = dict.get("username")
    if username == None:
        return None


    description = dict.get("description")
    followers = dict.get("followers")
    return Influencer(influencer_id=influencer_id, fullname=fullname,
                      username=username, description= description,
                      followers=followers)