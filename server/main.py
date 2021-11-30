import json
from flask import Flask, request, abort, current_app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///itp.sqlite"
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
  header = response.headers
  header['Access-Control-Allow-Origin'] = 'https://stepik.org'
  header['Access-Control-Allow-Headers'] = '*'
  return response

# models
class ProgrammingExercise(db.Model):
  __tablename__ = "p_exercises"
  id = db.Column(db.String(22), primary_key=True) # md5 hash of page url
  solution = db.Column(db.String, nullable=False)
  def serialize(self): return dict(solution=self.solution)

db.create_all()

# routes
@app.route('/', methods=["GET"])
def main():
  return 'cool'

@app.route('/solutions/<string:id>', methods=["GET"])
def get(id):
  pe = ProgrammingExercise.query.filter_by(id=id).first()
  if not pe: return abort(404)
  return json.dumps(pe.serialize()).replace("\\\\n", "\\n")

@app.route('/solutions/<string:id>', methods=["POST"])
def create(id):
  data = request.get_json()

  # validate
  if not data: return abort(400)
  solution = data['solution']
  if not solution: return abort(400)

  # if exists, delete
  if ProgrammingExercise.query.filter_by(id=id).first() != None:
    ProgrammingExercise.query.filter_by(id=id).delete()

  # add
  pe = ProgrammingExercise(id=id, solution=solution)
  db.session.add(pe)
  try: db.session.commit()
  except Exception as e:
    current_app.logger.error(e)
    db.session.rollback()
    return abort(500)

  # log
  current_app.logger.info(request.remote_addr + " added solution to " + id)

  return 'OK'

# run
app.run(port=6969)