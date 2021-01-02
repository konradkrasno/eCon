from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user
from app import db
from app.investments import bp
from app.investments.forms import InvestmentForm
from app.main.forms import WarrantyForm
from app.models import Investment, Worker


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.current_invest = Investment.get_current_invest(current_user)


@bp.route("/")
@login_required
def invest_list() -> str:
    investments = Investment.get_by_user_id(current_user.id)
    return render_template(
        "investments/investments.html",
        title="Investments",
        username=current_user.username,
        investments=investments,
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create() -> str:
    form = InvestmentForm()
    if form.validate_on_submit():
        investment = Investment(
            name=form.name.data,
            description=form.description.data,
            created_at=datetime.utcnow(),
        )
        worker = Worker(
            position="admin",
            admin=True,
            user_id=current_user.id,
        )
        investment.workers.append(worker)
        db.session.add(investment)
        db.session.commit()
        flash("You have created new investment successfully.")
        return redirect(url_for("investments.invest_list"))
    return render_template(
        "investments/form.html", title="Create Investment", form=form
    )


@bp.route("/<_id>")
@login_required
def info(_id: int) -> str:
    admin = Worker.is_admin(user_id=current_user.id, investment_id=_id)
    investment = Investment.query.filter_by(id=_id).first()
    return render_template(
        "investments/info.html", title="Investment", investment=investment, admin=admin
    )


@bp.route("choose/<_id>")
@login_required
def choose(_id: int) -> str:
    current_user.current_invest_id = _id
    db.session.commit()
    return redirect(url_for("investments.invest_list"))


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit() -> str:
    _id = request.args.get("_id")
    if not Worker.is_admin(user_id=current_user.id, investment_id=_id):
        return redirect(url_for("investments.info", _id=_id))
    investment = Investment.query.filter_by(id=_id).first()
    if investment:
        form = InvestmentForm()
        if form.validate_on_submit():
            investment.name = form.name.data
            investment.description = form.description.data
            db.session.commit()
            flash("You have edited the investment successfully.")
            return redirect(url_for("investments.info", _id=_id))
        elif request.method == "GET":
            form.name.data = investment.name
            form.description.data = investment.description
        return render_template(
            "investments/form.html", title="Edit Investment", form=form
        )
    return redirect(url_for("investments.invest_list"))


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete() -> str:
    _id = request.args.get("_id")
    if not Worker.is_admin(user_id=current_user.id, investment_id=_id):
        return redirect(url_for("investments.info", _id=_id))
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            return redirect(url_for("investments.info", _id=_id))
        if form.yes.data:
            Investment.query.filter_by(id=_id).delete()
            db.session.commit()
            flash("Investment has been deleted.")
            return redirect(url_for("investments.invest_list"))
    return render_template("warranty_form.html", title="Delete Investment", form=form)
