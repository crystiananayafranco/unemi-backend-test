from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc

# Definir la cadena de conexión a la base de datos
SQL_CONNECTION_STRING = ""

# Crear la aplicación Flask
app = Flask(__name__)

# Crear el motor de la base de datos
engine = create_engine(SQL_CONNECTION_STRING)

# Definir la función de conexión a la base de datos
def get_db_connection():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# Endpoint para crear un estudiante
@app.route('/students', methods=['POST'])
def create_student():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        major = data['major']

        session = get_db_connection()
        query = text("INSERT INTO students (name, email, major) VALUES (:name, :email, :major)")
        session.execute(query, {'name': name, 'email': email, 'major': major})
        session.commit()

        return jsonify({'message': 'Estudiante creado exitosamente'}), 201
    except KeyError:
        return jsonify({'message': 'Datos de estudiante incompletos o incorrectos'}), 400
    except sqlalchemy.exc.IntegrityError:
        return jsonify({'message': 'Error al crear estudiante. Conflicto de integridad de datos.'}), 409
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al crear estudiante'}), 500
    finally:
        session.close()

# Endpoint para obtener todos los estudiantes
@app.route('/students', methods=['GET'])
def get_students():
    try:
        session = get_db_connection()
        query = text("SELECT id, name, email, major FROM students")
        students = session.execute(query).fetchall()

        student_list = [
            {'id': student[0], 'name': student[1], 'email': student[2], 'major': student[3]}
            for student in students
        ]

        return jsonify({'students': student_list}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al obtener estudiantes'}), 500
    finally:
        session.close()

# Endpoint para actualizar un estudiante
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        major = data['major']

        session = get_db_connection()
        query = text("UPDATE students SET name = :name, email = :email, major = :major WHERE id = :id")
        session.execute(query, {'name': name, 'email': email, 'major': major, 'id': student_id})
        session.commit()

        return jsonify({'message': 'Estudiante actualizado exitosamente'}), 200
    except KeyError:
        return jsonify({'message': 'Datos de estudiante incompletos o incorrectos'}), 400
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al actualizar estudiante'}), 500
    finally:
        session.close()

# Endpoint para eliminar un estudiante
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        session = get_db_connection()
        query = text("DELETE FROM students WHERE id = :id")
        session.execute(query, {'id': student_id})
        session.commit()

        return jsonify({'message': 'Estudiante eliminado exitosamente'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al eliminar estudiante'}), 500
    finally:
        session.close()

# Empaquetar el código en un archivo ZIP para su implementación en Cloud Functions
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
