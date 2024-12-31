from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from models import db, User, Product, Cart, Order, UserLike
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from forms import LoginForm, RegisterForm, CheckoutForm,AddProductForm
import os

app = Flask(__name__, static_folder='static')
app.config.from_object('config.Config')
db.init_app(app)
csrf = CSRFProtect(app)  # Enable CSRF protection

# Initialize Migrate
migrate = Migrate(app, db)

# Mock data for Products
def get_products():
    return Product.query.all()

@app.route('/')
def home():
    return render_template('home.html', products=get_products())

@app.route('/store')
def store():
    categories = set(product.category for product in get_products())
    return render_template('store.html', products=get_products(), categories=categories)


@app.route('/product/<int:product_id>')
def product(product_id):
    # Get product information
    item = Product.query.get(product_id)
    if item is None:
        return "Product not found", 404

    # Check if the user is logged in and get the user information
    user = None
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()

    # Render template and pass product and user information
    return render_template('product.html', product=item, user=user)

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()

    # Get liked products and paginate them
    page = request.args.get('page', 1, type=int)
    liked_products = Product.query.join(UserLike).filter(UserLike.user_id == user.id).paginate(page=page, per_page=2, error_out=False)  # 2 items per page

    return render_template('profile.html', user=user, liked_products=liked_products.items, pagination=liked_products)

@app.route('/cart')
def cart_view():
    if 'user' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('login'))

    # Get cart items and paginate them
    page = request.args.get('page', 1, type=int)
    cart_items = Cart.query.filter_by(user_id=user.id).paginate(page=page, per_page=2, error_out=False)  # 2 items per page
    total = sum(item.product.price * item.quantity for item in cart_items.items)  # Use .items to get paginated data

    # Get liked products and paginate them
    liked_page = request.args.get('liked_page', 1, type=int)
    liked_products = user.liked_products.paginate(page=liked_page, per_page=2, error_out=False)  # 2 items per page

    return render_template('cart.html',
                           cart=cart_items.items,
                           total=total,
                           user=user,
                           liked_products=liked_products.items,
                           pagination=cart_items,
                           liked_pagination=liked_products)


@app.route('/add_to_cart/<int:product_id>', methods=['POST', 'GET'])
def add_to_cart(product_id):
    if 'user' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('store'))

    if product.stock <= 0:
        flash('Insufficient stock, cannot add to cart!', 'error')
        return redirect(url_for('store'))

    # Check if the product is already in the cart
    cart_item = Cart.query.filter_by(user_id=user.id, product_id=product.id).first()
    if cart_item:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1  # Increase quantity
        else:
            flash('Insufficient stock, cannot increase quantity!', 'error')
            return redirect(url_for('cart_view'))
    else:
        cart_item = Cart(user_id=user.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash('Product added to cart!', 'success')
    return redirect(url_for('cart_view'))

@app.route('/update_cart/<int:cart_item_id>/<action>', methods=['POST','GET'])
def update_cart(cart_item_id, action):
    if 'user' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('login'))

    # Find the cart item
    cart_item = Cart.query.get(cart_item_id)
    if not cart_item or cart_item.user_id != user.id:
        flash('Item not found in your cart!', 'error')
        return redirect(url_for('cart_view'))

    # Increase or decrease item quantity based on action
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            # If the item quantity is 1, delete it when the "-" button is clicked
            db.session.delete(cart_item)
            flash('Item removed from cart!', 'success')
            db.session.commit()
            return redirect(url_for('cart_view'))

    # Commit changes
    db.session.commit()
    flash(f'Item quantity {action}d successfully!', 'success')
    return redirect(url_for('cart_view'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()
    form = CheckoutForm()

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        contact = form.contact.data
        address = form.address.data
        cart_items = Cart.query.filter_by(user_id=user.id).all()

        # Check if stock is sufficient
        for item in cart_items:
            if item.quantity > item.product.stock:
                flash(f'Insufficient stock for: {item.product.name}', 'error')
                return redirect(url_for('cart_view'))

        # Update stock and clear cart
        for item in cart_items:
            item.product.stock -= item.quantity
            db.session.delete(item)

        # Create order
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = Order(user_id=user.id, total_price=total_price)
        db.session.add(order)
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('cart_view'))

    return render_template('checkout.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # 用户认证
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user'] = username
            if user.is_admin:
                session['is_admin'] = True
            else:
                session['is_admin'] = False
            flash('登录成功！', 'success')
            return redirect(url_for('add_product'))  # 在登录成功后直接跳转到添加商品页面
        else:
            flash('用户名或密码错误！', 'error')
    return render_template('login.html', form=form)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        price = form.price.data
        category = form.category.data

        # Set default image to 'error.png' if no image is provided
        image = form.image.data if form.image.data else 'nothing.png'  # Use 'error.png' if no image is provided
        image2 = form.image2.data if form.image2.data else image  # Use 'image' if 'image2' is not provided

        # Check if the image file actually exists, if not, use error.png
        static_folder = os.path.join(app.root_path, 'static')

        # Check if the image exists in the static folder
        if not os.path.isfile(os.path.join(static_folder, 'images', image)):
            image = 'error.png'  # Fallback to error.png if the image does not exist

        # Check if image2 exists, if not fallback to image
        if not os.path.isfile(os.path.join(static_folder, 'images', image2)):
            image2 = image  # Fallback to image if image2 does not exist

        stock = form.stock.data

        # Create new product and save it to the database
        new_product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            image=image,
            image2=image2,
            stock=stock
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Add successfully', 'success')
        return redirect(url_for('store'))

    return render_template('add_product.html', form=form)


@app.route('/delete_product/<int:product_id>', methods=['POST','GET'])
def delete_product(product_id):
    # 确保用户是管理员
    if 'is_admin' not in session or not session['is_admin']:
        flash('您没有权限删除商品', 'error')
        return redirect(url_for('store'))

    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('商品已删除', 'success')
    else:
        flash('商品未找到', 'error')

    return redirect(url_for('store'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # Check if form is valid
        username = form.username.data
        password = form.password.data
        email = form.email.data

        # Check if the username exists
        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        # Check if the email suffix is valid
        allowed_suffixes = ['qq.com', 'leeds.ac.uk', '163.com']
        email_suffix = email.split('@')[-1]
        if email_suffix not in allowed_suffixes:
            flash('Invalid email domain! Please use qq.com, leeds.ac.uk, or 163.com.', 'error')
            return redirect(url_for('register'))

        # Check if the email exists
        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))

        # If no issues, create a new user
        user = User(username=username, email=email)
        user.set_password(password)  # Set password
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    else:
        # If form is not valid, show error messages
        print("Form did not validate.")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'error')

    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))  # Ensure we go to home after logout, where navbar will reflect this

@app.route('/like_product/<int:product_id>', methods=['POST','GET'])
def like_product(product_id):
    print("Like request received for product_id:", product_id)

    # Check if the user is logged in
    if 'user' not in session:
        print("User not logged in!")
        return jsonify({'success': False, 'message': 'Please log in first!'}), 400

    user = User.query.filter_by(username=session['user']).first()
    product = Product.query.get(product_id)

    if not product:
        print(f"Product {product_id} not found!")
        return jsonify({'success': False, 'message': 'Product not found!'}), 404

    csrf_token = request.headers.get('X-CSRFToken')
    print(f"Received CSRF token: {csrf_token}, Session CSRF token: {session.get('csrf_token')}")

    # CSRF Token validation
    if not csrf_token or csrf_token != session.get('csrf_token'):
        print("Invalid CSRF token!")
        return jsonify({'success': False, 'message': 'Invalid CSRF token!'}), 400

    # Check if the user has already liked the product
    existing_like = UserLike.query.filter_by(user_id=user.id, product_id=product.id).first()
    if existing_like:
        print("Product already liked!")
        return jsonify({'success': False, 'message': 'You have already liked this product!'}), 400

    # Handle the like action
    new_like = UserLike(user_id=user.id, product_id=product.id)
    db.session.add(new_like)
    db.session.commit()

    print(f"Product {product_id} liked successfully!")
    return jsonify({'success': True, 'message': 'Product added to your liked products!'}), 200

@app.route('/unlike_product/<int:product_id>', methods=['POST','GET'])
def unlike_product(product_id):
    print("Unlike request received for product_id:", product_id)

    if 'user' not in session:
        print("User not logged in!")
        return jsonify({'success': False, 'message': 'Please log in first!'}), 400

    user = User.query.filter_by(username=session['user']).first()
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'success': False, 'message': 'Product not found!'}), 404

    csrf_token = request.headers.get('X-CSRFToken')
    if not csrf_token or csrf_token != session.get('csrf_token'):
        print("Invalid CSRF token!")
        return jsonify({'success': False, 'message': 'Invalid CSRF token!'}), 400

    like = UserLike.query.filter_by(user_id=user.id, product_id=product.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product removed from your liked products!'}), 200
    else:
        return jsonify({'success': False, 'message': 'You have not liked this product!'}), 400

@app.before_request
def set_csrf_token():
    """
    Generate and store CSRF token in session before each request
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = os.urandom(24).hex()
    print("CSRF Token set:", session['csrf_token'])


if __name__ == '__main__':
    app.run(debug=True)
