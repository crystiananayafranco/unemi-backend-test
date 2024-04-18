from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text, exc, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
import os

from marshmallow import Schema, fields, ValidationError
from dotenv import load_dotenv

# Load configuration from environment variables
from dotenv import load_dotenv
load_dotenv()
SQL_CONNECTION_STRING = os.getenv('SQL_CONNECTION_STRING')

app = Flask(__name__)
engine = create_engine(SQL_CONNECTION_STRING)

# SQLAlchemy Model Definition
Base = declarative_base()


class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    major = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Student Schema (for data validation)
class StudentSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    major = fields.Str(required=True)


# Database Connection Helper
def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


# Service Functions
def create_student(student_data):
    student = Student(**student_data)
    session = get_db_session()
    session.add(student)
    session.commit()
    student_dict = student.as_dict()  # Convert to dictionary
    session.close()
    return student


def get_all_students():
    session = get_db_session()
    students = session.query(Student).all()
    session.close()
    return students


# ... (add functions for update and delete)

# Routes
@app.route('/students', methods=['POST'])
def create_student_endpoint():
    try:
        student_data = StudentSchema().load(request.get_json())
        student = create_student(student_data)
        return jsonify(student.as_dict()), 201
    except ValidationError as err:
        return jsonify({'message': err.messages}), 400
    except IntegrityError as e:
        return jsonify({'message': 'Error: Posible email duplicado'}), 409
    except Exception as e:
        print("Error in create_student_endpoint:", e)  # Log the error
        return jsonify({'message': 'Error al crear estudiante'}), 500


@app.route('/students', methods=['GET'])
def get_students_endpoint():
    students = get_all_students()
    student_list = [student.as_dict() for student in students]
    return jsonify({'students': student_list}), 200


# ... add routes for '/students/<int:student_id>' using PUT, DELETE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
