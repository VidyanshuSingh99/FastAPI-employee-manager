from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from database import get_connection, init_db
from schemas import EmployeeCreate, EmployeeOut

app = FastAPI(title="Employee CRUD")
templates = Jinja2Templates(directory="templates")  


@app.on_event("startup")
def startup():
    init_db()


##--------------- create employee-----------------##

@app.post("/employees", response_model=EmployeeOut, status_code=201, tags=["API"])
def create_employee(emp: EmployeeCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO employees (name, department, salary) VALUES (%s, %s, %s) RETURNING *",
                (emp.name, emp.department, emp.salary),
            )
            row = cur.fetchone()
        conn.commit()
        return dict(row)
    finally:
        conn.close()


##----------------read all employees detail---------------##

@app.get("/employees", response_model=list[EmployeeOut], tags=["API"])
def list_employees():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees ORDER BY id")
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


##------------------display single particular employee--------------##
@app.get("/employees/{emp_id}", response_model=EmployeeOut, tags=["API"])
def get_employee(emp_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Employee not found")
        return dict(row)
    finally:
        conn.close()


##---------------for updating the details of Employee--------------##

@app.put("/employees/{emp_id}", response_model=EmployeeOut, tags=["API"])
def update_employee(emp_id: int, emp: EmployeeCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE employees
                   SET name=%s, department=%s, salary=%s
                   WHERE id=%s RETURNING *""",
                (emp.name, emp.department, emp.salary, emp_id),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Employee not found")
        conn.commit()
        return dict(row)
    finally:
        conn.close()



##----------------for deleting the employee details------------------##

@app.delete("/employees/{emp_id}", tags=["API"])
def delete_employee(emp_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM employees WHERE id=%s RETURNING id", (emp_id,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Employee not found")
        conn.commit()
        return {"message": f"Employee {emp_id} deleted"}
    finally:
        conn.close()



@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request, msg: Optional[str] = None):
    """List all employees and show the add-employee form."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees ORDER BY id")
            employees = cur.fetchall()
    finally:
        conn.close()
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "employees": employees,
        "msg": msg
    }
    )


##--------------for editing the form-------------##

@app.get("/edit/{emp_id}", response_class=HTMLResponse, include_in_schema=False)
def edit_form(request: Request, emp_id: int):
    """Show the pre-filled edit form for a single employee."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
            emp = cur.fetchone()
    finally:
        conn.close()
    if not emp:
        return RedirectResponse("/?msg=Employee+not+found", status_code=303)
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "employees": _all_employees(),
        "edit_emp": emp,
        "msg": None,
    },
)


##-----------------form creation---------------##

@app.post("/form/create", include_in_schema=False)
def form_create(
    name: str = Form(...),
    department: str = Form(...),
    salary: int = Form(...),
):
    emp = EmployeeCreate(name=name, department=department, salary=salary)
    create_employee(emp)
    return RedirectResponse("/?msg=Employee+added", status_code=303)



##----------------form updation--------------------##

@app.post("/form/update/{emp_id}", include_in_schema=False)
def form_update(
    emp_id: int,
    name: str = Form(...),
    department: str = Form(...),
    salary: int = Form(...),
):
    emp = EmployeeCreate(name=name, department=department, salary=salary)
    update_employee(emp_id, emp)
    return RedirectResponse("/?msg=Employee+updated", status_code=303)



##--------------form deletion-------------------##

@app.post("/form/delete/{emp_id}", include_in_schema=False)
def form_delete(emp_id: int):
    delete_employee(emp_id)
    return RedirectResponse("/?msg=Employee+deleted", status_code=303)


##--------------to get all employees detail--------------##
def _all_employees():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees ORDER BY id")
            return cur.fetchall()
    finally:
        conn.close()
