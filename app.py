from flask import Flask, render_template , request ,session
from flask_session import Session
import psycopg2

app = Flask(__name__,static_folder='./static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = psycopg2.connect( user="postgres",
                         password="positiveiam123",
                         host = "localhost",
                         port="5432",
                         database="postgres"
                         )

cur = conn.cursor()



@app.route("/")
def index():
    return render_template("index.html",usersigned =0 , samepassword =0 ,signsuccess =0,loginfail=0)

@app.route("/sign" , methods = ["POST"])
def sign():
    emaill = request.form.get("signupemail")
    password1 = request.form.get("signuppassword1")
    password2 = request.form.get("signuppassword2")
    cur.execute(f"select case when exists(select * from users where email ='{emaill}') then 1 else 0 end;" )
    tns = cur.fetchall()
    ans = tns[0][0]
    if(ans==0 and  password1== password2):
        cur.execute(f"insert into users values('{emaill}','{password1}');")
        conn.commit()
        return render_template("index.html",usersigned =0 , samepassword =0,signsuccess=1,loginfail=0,loginsuccess=0)

    else:
        if (ans==1):
            return render_template("index.html",usersigned =1 , samepassword =0,signsuccess=0,loginfail=0,loginsuccess=0)
        else:
            return render_template("index.html",usersigned =0 , samepassword =1,signsuccess=0,loginfail=0,loginsuccess=0)

@app.route("/log" , methods = ["POST"])
def log():
        emaill = request.form.get("loginemail")
        pasword = request.form.get("loginpassword")
        cur.execute(f"select case when exists(select * from users where email ='{emaill}' and password = '{pasword}') then 1 else 0 end;" )
        tns = cur.fetchall()
        ans = tns[0][0]
        if(ans==1):
            session["user"] = emaill
            return render_template("index.html",usersigned =0 , samepassword =0,signsuccess=0,loginfail=0,loginsuccess=1)
            
        else:
            return render_template("index.html",usersigned =0 , samepassword =0,signsuccess=0,loginfail=1,loginsuccess=0)


@app.route("/home" )
def home():
        if(session.get("user") == None):
            return render_template("none.html")
        else :
            return render_template("home.html",user = session.get("user"))
   

@app.route("/artists")
def artists():
    cur.execute("SELECT artists FROM data_each_artist GROUP BY artists ORDER BY artists ASC;")
    artists=cur.fetchall()
    return render_template("artists.html",Artists = artists)

  


@app.route("/add/<string:sng>/<string:art>/<int:yr>")
def add(sng,art,yr):
    emaill = session.get("user")
    cur.execute(f"select case when exists(select * from playlists where email ='{emaill}'  and name ='{sng}' and year={yr} and artist='{art}') then 1 else 0 end;" )
    tns = cur.fetchall()
    ans = tns[0][0]
    if(ans==0):
        cur.execute(f"insert into  playlists values('{sng}','{art}',{yr},'{emaill}');")
        conn.commit()
        songs=session.get("songs")
        return render_template("songs.html",Songs = songs ,already=0,added=1)
    else:
        songs = session.get("songs")
        return render_template("songs.html",Songs = songs ,already=1,added=0)
        

@app.route("/playlist")
def playlist():
    usr = session.get("user")
    cur.execute(f"select  name ,artist,year from playlists   where email ='{usr}' ;")
    songs=cur.fetchall()
    return render_template("playlist.html",Songs = songs,removed=0)
   
@app.route("/remove/<string:sng>/<string:art>/<int:yr>")
def remove(sng,art,yr):
    emaill = session.get("user")
    cur.execute(f"delete from playlists where email ='{emaill}'  and name ='{sng}' and artist ='{art}' and year={yr};" )
    conn.commit()
    cur.execute(f"select  name ,artist,year from playlists    where email ='{emaill}' ;")
    songs=cur.fetchall()
    return render_template("playlist.html",Songs = songs ,removed=1)
        

@app.route("/quiz")
def quiz():
    cur.execute("select * from quiz order by random() limit 6;")
    questions = cur.fetchall()
    session["questions"] = questions
    return render_template("quiz.html",Questions=questions)  

@app.route("/quizresult" , methods = ["POST","GET"])
def quizresult():
    if request.method=="POST":
        value1=request.form["1"]
        value2=request.form["2"]
        value3=request.form["3"]
        value4=request.form["4"]
        value5=request.form["5"]
        value6=request.form["6"]
        que = session.get("questions")
        ans1= que[0][6]
        anss1 = f"{ans1}"
        ans2= que[1][6]
        anss2 = f"{ans2}"
        ans3= que[2][6]
        anss3 = f"{ans3}"
        ans4= que[3][6]
        anss4 = f"{ans4}"
        ans5= que[4][6]
        anss5 = f"{ans5}"
        ans6= que[5][6]
        anss6 = f"{ans6}"
        score =0
        if(value1==anss1):
            score=score+1
        if(value2==anss2):
            score=score+1
        if(value3==anss3):
            score=score+1
        if(value4==anss4):
            score=score+1
        if(value5==anss5):
            score=score+1
        if(value6==anss6):
            score=score+1
        emaill = session.get("user")
        cur.execute(f"insert into leaderboard values('{emaill}',{score});")
        conn.commit()
        cur.execute("select * from leaderboard order by score desc;")
        leaders = cur.fetchall()
        return render_template("leaderboard.html",Leaders=leaders,Score=score)
    else:
        cur.execute("select * from leaderboard order by score desc;")
        leaders = cur.fetchall()
        return render_template("leaderboard.html",Leaders=leaders,Score=0)



@app.route("/artistsong/<string:artist>")
def artistsong(artist):
    cur.execute(f"select data.name ,'{artist}' as artist,data.year from data where data.artists like '%{artist}%';")
    songs=cur.fetchall()
    session["songs"] = songs
    return render_template("songs.html",Songs=songs)
        
            
@app.route("/topcharts")
def topcharts():
    cur.execute("select distinct year from data_by_year order by year desc;")
    years=cur.fetchall()
    return render_template("topcharts.html",Years =years)

@app.route("/topchartsyear/<int:year>")
def topchartsyear(year):
    cur.execute(f"SELECT data_each_artist.name, MIN(data_each_artist.artists) as artists, {year} as year \
FROM data_each_artist \
WHERE data_each_artist.year = {year} \
GROUP BY data_each_artist.name, data_each_artist.year, data_each_artist.popularity \
ORDER BY data_each_artist.popularity DESC \
LIMIT 20;")
    songs=cur.fetchall()
    session["songs"] = songs
    return render_template("songs.html",Songs=songs)


@app.route("/years")
def years():
    cur.execute("select distinct year from data_by_year order by year desc;")
    years=cur.fetchall()
    return render_template("years.html",Years =years)

@app.route("/songssyear/<int:year>")
def songsyear(year):
    cur.execute(f"SELECT data_each_artist.name, MIN(data_each_artist.artists) as artists, {year} as year \
FROM data_each_artist \
WHERE data_each_artist.year = {year} \
GROUP BY data_each_artist.name, data_each_artist.year, data_each_artist.popularity \
ORDER BY data_each_artist.popularity DESC ;")
    songs=cur.fetchall()
    session["songs"] = songs
    return render_template("songs.html",Songs=songs)