from app import app, db, Product

# Push the application context
with app.app_context():
    # Retrieve all Product data
    products = Product.query.all()

    # Print out the image fields for each product
    for product in products:
        print(f"Product Name: {product.name}")
        print(f"Image 1: {product.image}")
        print(f"Image 2: {product.image2}")
    db.session.commit()
    print("Product details updated to English in the database!")
