import datetime
from flask import render_template, redirect, url_for, flash, g, request
from flask_login import login_required, current_user
from app import db
from app.tasks import bp
from app.models import Task, Worker
from app.tasks.forms import TaskForm, ProgressForm
from app.main.forms import WarrantyForm


@bp.route("/")
@login_required
def tasks():
    tasks = Task.get_all(invest_id=g.current_invest.id)
    admin = Worker.is_admin(user_id=current_user.id, investment_id=g.current_invest.id)
    next_page = url_for("tasks.tasks")
    return render_template(
        "tasks/tasks.html", title="Tasks", tasks=tasks, admin=admin, next_page=next_page
    )


@bp.route("/my")
@login_required
def my_tasks():
    tasks = Worker.get_by_username(
        invest_id=g.current_invest.id, username=current_user.username
    ).tasks_to_execution.order_by(Task.deadline).order_by(Task.priority.desc()).all()
    admin = Worker.is_admin(user_id=current_user.id, investment_id=g.current_invest.id)
    next_page = url_for("tasks.my_tasks")
    return render_template(
        "tasks/tasks.html",
        title="My Tasks",
        tasks=tasks,
        admin=admin,
        next_page=next_page,
    )


@bp.route("/deputed")
@login_required
def deputed_tasks():
    tasks = Worker.get_by_username(
        invest_id=g.current_invest.id, username=current_user.username
    ).deputed_tasks.order_by(Task.deadline).order_by(Task.priority.desc()).all()
    admin = Worker.is_admin(user_id=current_user.id, investment_id=g.current_invest.id)
    next_page = url_for("tasks.deputed_tasks")
    return render_template(
        "tasks/tasks.html",
        title="Deputed Tasks",
        tasks=tasks,
        admin=admin,
        next_page=next_page,
    )


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_task():
    orderer = Worker.get_by_username(g.current_invest.id, current_user.username)
    if not orderer:
        flash("Choose investment first.")
        return redirect(url_for("tasks.tasks"))
    form = TaskForm()
    if form.validate_on_submit():
        executor = Worker.get_by_username(g.current_invest.id, form.executor_name.data)
        db.session.add(
            Task(
                description=form.description.data,
                created_at=datetime.datetime.utcnow(),
                deadline=form.deadline.data,
                priority=form.priority.data,
                orderer=orderer,
                executor=executor,
                progress=0,
                investment_id=g.current_invest.id,
            )
        )
        db.session.commit()
        flash("You have created the task successfully.")
        return redirect(url_for("tasks.tasks"))
    return render_template("tasks/form.html", title="Add Task", form=form)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_task():
    _id = request.args.get("_id")
    next_page = request.args.get("next_page")
    if not next_page:
        next_page = url_for("tasks.tasks")
    task = Task.query.get(int(_id))
    if task:
        form = TaskForm()
        if form.validate_on_submit():
            task.description = form.description.data
            task.deadline = form.deadline.data
            task.priority = form.priority.data
            if form.executor_name != task.executor.users.username:
                task.executor = Worker.get_by_username(
                    invest_id=g.current_invest.id, username=form.executor_name.data
                )
            db.session.commit()
            flash("You have edited the task successfully.")
            return redirect(next_page)
        elif request.method == "GET":
            form.description.data = task.description
            form.deadline.data = task.deadline
            form.priority.data = task.priority
            form.executor_name.data = task.executor.users.username
        return render_template("tasks/form.html", title="Edit Task", form=form)
    return redirect(next_page)


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete_task():
    _id = request.args.get("_id")
    next_page = request.args.get("next_page")
    if not next_page:
        next_page = url_for("tasks.tasks")
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            flash("The task has not been deleted.")
        elif form.yes.data:
            Task.query.filter_by(id=_id).delete()
            db.session.commit()
            flash("You have deleted the task successfully.")
        return redirect(next_page)
    return render_template("warranty_form.html", title="Delete Task", form=form)


@bp.route("/change", methods=["GET", "POST"])
@login_required
def change_progress():
    _id = request.args.get("_id")
    next_page = request.args.get("next_page")
    if not next_page:
        next_page = url_for("tasks.tasks")
    task = Task.query.get(int(_id))
    if task:
        form = ProgressForm()
        if form.validate_on_submit():
            task.progress = form.progress.data
            db.session.commit()
            flash("You have changed the progress successfully.")
            return redirect(next_page)
        elif request.method == "GET":
            form.progress.data = task.progress
        return render_template("tasks/form.html", title="Change Progress", form=form)
    return redirect(next_page)
