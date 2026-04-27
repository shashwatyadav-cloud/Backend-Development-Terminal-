from fastapi import FastAPI,HTTPException,Depends
from schema import StudentCreate,StudentResponse,StudentUpdate
from database import get_db,Base,engine
from sqlalchemy.orm import Session
from models import Student
import redis,json

app = FastAPI()

Base.metadata.create_all(bind=engine)

redis_client = redis.Redis(host="localhost",port=6379,decode_responses=True)

@app.post("/student",response_model=StudentResponse)
def create_student(student:StudentCreate,db:Session = Depends(get_db)):
    
    new_student = Student(name = student.name,age = student.age)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    

    return new_student

@app.get("/",response_model=list[StudentResponse])
def get_students(db:Session = Depends(get_db)):
    students = db.query(Student).all()
    return students

@app.get("/student/{id}",response_model=StudentResponse)
def get_single_student(id:int,db:Session = Depends(get_db)):   
    cached_student = redis_client.get(f"student_{id}")

    if cached_student:
        return json.loads(cached_student)

    student = db.query(Student).filter(Student.id == id).first()

    if not student:
        return None

    student_data = {"id": student.id,"name": student.name,"age": student.age}

    redis_client.set(f"student_{id}",json.dumps(student_data),ex=60)

    return student_data

    

@app.put("/student/{id}",response_model=StudentResponse)
def update_student(id:int,student: StudentCreate,db:Session = Depends(get_db)):
    
    update_student = db.query(Student).filter(Student.id == id).first()
    if update_student is None:
        raise HTTPException(status_code=404,detail="student not found")
    update_student.name = student.name
    update_student.age = student.age 
    db.commit()
    db.refresh(update_student)

    return update_student




@app.delete("/student/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="student not found")

    db.delete(student)
    db.commit()

    return {"message": "student deleted successfully"}


@app.patch("/student/{id}", response_model=StudentResponse)
def patch_student(id: int,student: StudentUpdate,db: Session = Depends(get_db)):
    update_student = db.query(Student).filter(Student.id == id).first()

    if update_student is None:
        raise HTTPException(status_code=404, detail="student not found")

    if student.name is not None:
        update_student.name = student.name

    if student.age is not None:
        update_student.age = student.age

    db.commit()
    db.refresh(update_student)

    return update_student



# @app.delete("/student/{student_id}")
# def delete_student(student_id:int):
#     if student_id in db:
#         raise HTTPException(status_code=400,detail="student not found")
    
#     print(db)
#     deleted = db.pop(student_id)
#     print(deleted)
#     print(db)

#     return {"message":"Student deleted","data":deleted}