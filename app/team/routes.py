import uuid

from flask import render_template, redirect, url_for, flash, g, request
from flask_login import login_required, current_user

from app import db
from app.auth import email
from app.main.forms import WarrantyForm
from app.models import Worker, User, Investment
from app.team import bp
from app.team.forms import CreateWorkerForm, EditWorkerForm


@bp.route("/")
@login_required
def team():
    admin = Worker.is_admin(current_user.id, g.current_invest.id)
    team = Worker.get_team(investment_id=g.current_invest.id)
    return render_template("team/team.html", title="Team", team=team, admin=admin)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_worker() -> str:
    if not Worker.is_admin(current_user.id, g.current_invest.id):
        return redirect(url_for("team.team"))
    form = CreateWorkerForm()
    if form.validate_on_submit():
        if Worker.belongs_to_investment(form.email.data, g.current_invest.id):
            flash("This user is already added to workers.")
            return redirect(url_for("team.team"))
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            user = User(
                username=form.email.data,
                email=form.email.data,
                password=uuid.uuid4().hex,
            )
            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(email=form.email.data).first()
            email.send_complete_registration_mail(user)
        worker = Worker(
            position=form.position.data,
            admin=form.admin.data,
            user_id=user.id,
        )
        g.current_invest.workers.append(worker)
        db.session.commit()
        flash("You have added new worker successfully.")
        return redirect(url_for("team.team"))
    return render_template("team/form.html", title="Add Worker", form=form)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_worker() -> str:
    _id = request.args.get("_id")
    if not Worker.is_admin(current_user.id, g.current_invest.id):
        return redirect(url_for("team.team"))
    worker = Worker.query.filter_by(id=_id).first()
    if worker:
        form = EditWorkerForm()
        if form.validate_on_submit():
            worker.position = form.position.data
            db.session.commit()
            flash("You have edited the information about the worker successfully.")
            return redirect(url_for("team.team"))
        elif request.method == "GET":
            form.position.data = worker.position
        return render_template("team/form.html", title="Edit Worker", form=form)
    return redirect(url_for("teat.team"))


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete_worker() -> str:
    _id = request.args.get("_id")
    if not Worker.is_admin(current_user.id, g.current_invest.id):
        return redirect(url_for("team.team"))
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.yes.data:
            worker = Worker.query.filter_by(id=_id).first()
            if worker:
                if worker.user_id != current_user.id:
                    db.session.delete(worker)
                    db.session.commit()
                    flash("You have been deleted worker successfully.")
                else:
                    flash("You can not delete yourself!")
        return redirect(url_for("team.team"))
    return render_template("warranty_form.html", title="Delete Worker", form=form)


@bp.route("/root_permission", methods=["GET", "POST"])
@login_required
def change_root_permission():
    _id = request.args.get("_id")
    if Worker.is_admin(current_user.id, g.current_invest.id):
        worker = Worker.query.filter_by(id=_id).first()
        if worker:
            num_of_admins = Investment.get_num_of_admins(g.current_invest.id)
            if num_of_admins < 2:
                if worker.admin:
                    flash("You can not delete last admin!")
                    return redirect(url_for("team.team"))
            form = WarrantyForm()
            if form.validate_on_submit():
                if form.yes.data:
                    if worker.admin:
                        worker.admin = False
                    else:
                        worker.admin = True
                    db.session.commit()
                    flash("You have changed worker's root permission successfully.")
                return redirect(url_for("team.team"))
            return render_template(
                "warranty_form.html", title="Change Root Permission", form=form
            )
    return redirect(url_for("team.team"))
