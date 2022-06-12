from market import app
from market.models import Item, User
from flask import render_template, url_for, redirect, request, flash
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user
from market import db


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    if request.method == "POST":
        purchased_item = request.form.get('purchased_item')
        purchased_item_object = Item.query.filter_by(name=purchased_item).first()

        if purchased_item_object:
            if current_user.can_purchase(purchased_item_object):
                purchased_item_object.buy(current_user)
                flash(f" You purchased {purchased_item_object.name} for {purchased_item_object.price}$", category='success')
            else:
                flash(f"You Can't Buy {purchased_item_object.name}!", category='danger')
        sold_item = request.form.get('sold_item')
        sold_item_object = Item.query.filter_by(name=sold_item).first()

        if sold_item_object:
            if current_user.can_sell(sold_item_object):
                sold_item_object.sell(current_user)
                flash(f"Congratulations! You sold {sold_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {sold_item_object.name}", category='danger')

        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email.data,
                              password=form.password.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Registration went successfully! Welcome {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))

    if form.errors != {}:
        for error_message in form.errors.values():
            flash(f'Something Went Wrong! Unable To Create: {error_message}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Welcome Again: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username And Password Is Incorrect! Please Try Again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You Have Been Logged Out!", category='info')
    return redirect(url_for("home_page"))










