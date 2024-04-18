from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text, exc, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
import os

from marshmallow import Schema, fields, ValidationError
from dotenv import load_dotenv

load_dotenv()
SQL_CONNECTION_STRING = os.getenv('SQL_CONNECTION_STRING')

app = Flask(__name__)
engine = create_engine(SQL_CONNECTION_STRING)

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    major = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class StudentSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    major = fields.Str(required=True)

def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()

def create_student(student_data):
    student = Student(**student_data)
    session = get_db_session()
    session.add(student)
    session.commit()
    session.close()
    return student

def get_all_students():
    session = get_db_session()
    students = session.query(Student).all()
    session.close()
    return students

def get_student(student_id):
    session = get_db_session()
    student = session.query(Student).get(student_id)
    session.close()
    return student

def update_student(student_id, student_data):
    session = get_db_session()
    student = session.query(Student).get(student_id)
    if student:
        for key, value in student_data.items():
            setattr(student, key, value)
        session.commit()
    session.close()
    return student

def delete_student(student_id):
    session = get_db_session()
    student = session.query(Student).get(student_id)
    if student:
        session.delete(student)
        session.commit()
    session.close()
    return student

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
        return jsonify({'message': 'Error al crear estudiante'}), 500

@app.route('/students', methods=['GET'])
def get_students_endpoint():
    students = get_all_students()
    student_list = [student.as_dict() for student in students]
    return jsonify({'students': student_list}), 200

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student_endpoint(student_id):
    student = get_student(student_id)
    if student:
        return jsonify(student.as_dict()), 200
    else:
        return jsonify({'message': 'Student not found'}), 404

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student_endpoint(student_id):
    try:
        student_data = StudentSchema().load(request.get_json())
        student = update_student(student_id, student_data)
        if student:
            return jsonify(student.as_dict()), 200
        else:
            return jsonify({'message': 'Student not found'}), 404
    except ValidationError as err:
        return jsonify({'message': err.messages}), 400
    except Exception as e:
        return jsonify({'message': f"Error updating student: {e}"}), 500

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student_endpoint(student_id):
    student = delete_student(student_id)
    if student:
        return jsonify({'message': 'Student deleted successfully'}), 200
    else:
        return jsonify({'message': 'Student not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
