import json
import os
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort
)
from config import (
    SECRET_KEY, DATABASE_URL, STORE_NAME, STORE_TAGLINE,
    AMAZON_PARTNER_TAG, CATEGORIES, OPENAI_API_KEY
)
from models import db, Product, ClickLog, Order, Visitor

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def seed_products():
    if Product.query.count() > 0:
        return
    products = [
        {
            "name": "Wireless Earbuds Pro X1",
            "slug": "wireless-earbuds-pro-x1",
            "price": 29.99,
            "old_price": 59.99,
            "category": "electronics",
            "badge": "BEST SELLER",
            "is_featured": True,
            "is_trending": True,
            "rating": 4.8,
            "reviews_count": 15420,
            "short_description": "Crystal clear sound with 40-hour battery life. Noise cancelling technology.",
            "description": "Experience studio-quality sound with our Wireless Earbuds Pro X1. Featuring advanced noise cancellation, 40-hour battery life, and IPX7 waterproof rating. Perfect for workouts, commuting, or just enjoying your favorite music. Over 15,000 five-star reviews can't be wrong!",
            "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B09V3KXJPB?tag=" + AMAZON_PARTNER_TAG,
            "tags": "earbuds,wireless,music,noise cancelling",
            "meta_title": "Wireless Earbuds Pro X1 - Best Sound Under $30",
            "meta_description": "Crystal clear wireless earbuds with 40-hour battery. 15,000+ five-star reviews. Order now!",
        },
        {
            "name": "Smart LED Strip Lights 10m",
            "slug": "smart-led-strip-lights",
            "price": 19.99,
            "old_price": 39.99,
            "category": "home-kitchen",
            "badge": "TRENDING",
            "is_featured": True,
            "is_trending": True,
            "rating": 4.7,
            "reviews_count": 42300,
            "short_description": "Transform any room with 16 million color options. App controlled.",
            "description": "Turn your room into a vibe with Smart LED Strip Lights. 16 million colors, music sync mode, and app control. Easy peel-and-stick installation. Perfect for bedrooms, gaming setups, or parties. Over 42,000 satisfied customers!",
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B09BL5GJ3M?tag=" + AMAZON_PARTNER_TAG,
            "tags": "led lights,smart home,room decor,gaming",
            "meta_title": "Smart LED Strip Lights - 16M Colors | $19.99",
            "meta_description": "Transform your room with 16 million color LED lights. App controlled, music sync. Order now!",
        },
        {
            "name": "Portable Charger 20000mAh",
            "slug": "portable-charger-20000mah",
            "price": 24.99,
            "old_price": 44.99,
            "category": "electronics",
            "badge": "HOT DEAL",
            "is_featured": True,
            "is_trending": False,
            "rating": 4.8,
            "reviews_count": 8900,
            "short_description": "Charge your phone 5 times. Fast charging USB-C. Ultra slim design.",
            "description": "Never run out of battery again with our 20000mAh Portable Charger. Charges your phone up to 5 times. Features dual USB ports, fast charging, and LED indicator. Ultra-slim design fits in your pocket.",
            "image_url": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B08N3MNGQ2?tag=" + AMAZON_PARTNER_TAG,
            "tags": "charger,portable,battery,travel",
            "meta_title": "Portable Charger 20000mAh - Charge 5X | $24.99",
            "meta_description": "20000mAh portable charger - charge your phone 5 times. Fast charging. Order now!",
        },
        {
            "name": "Resistance Bands Set - 5 Levels",
            "slug": "resistance-bands-set",
            "price": 15.99,
            "old_price": 29.99,
            "category": "fitness",
            "badge": "",
            "is_featured": False,
            "is_trending": True,
            "rating": 4.6,
            "reviews_count": 31200,
            "short_description": "Complete home gym setup. 5 resistance levels. Carry bag included.",
            "description": "Get a full-body workout at home with our Resistance Bands Set. 5 different resistance levels from beginner to advanced. Includes carrying bag, door anchor, and exercise guide. Join 31,000+ people who transformed their fitness!",
            "image_url": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B07Y4V7T3Y?tag=" + AMAZON_PARTNER_TAG,
            "tags": "fitness,workout,gym,exercise",
            "meta_title": "Resistance Bands Set - 5 Levels | Home Gym | $15.99",
            "meta_description": "5-level resistance bands for home workouts. 31,000+ reviews. Order now!",
        },
        {
            "name": "Automatic Pet Feeder WiFi",
            "slug": "automatic-pet-feeder-wifi",
            "price": 49.99,
            "old_price": 89.99,
            "category": "pets",
            "badge": "EDITOR PICK",
            "is_featured": True,
            "is_trending": True,
            "rating": 4.7,
            "reviews_count": 6800,
            "short_description": "Feed your pet from anywhere. App control. Voice recording feature.",
            "description": "Never worry about feeding your pet again. Our WiFi Automatic Pet Feeder lets you schedule meals, record voice calls, and monitor portions from your phone. 6L capacity holds a week of food. Your pet deserves the best!",
            "image_url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B08DKZSC47?tag=" + AMAZON_PARTNER_TAG,
            "tags": "pet feeder,cat,dog,smart pet",
            "meta_title": "WiFi Automatic Pet Feeder - App Control | $49.99",
            "meta_description": "Feed your pet from anywhere with WiFi control. 6L capacity. Voice recording. Order now!",
        },
        {
            "name": "Posture Corrector Brace",
            "slug": "posture-corrector-brace",
            "price": 18.99,
            "old_price": 34.99,
            "category": "fitness",
            "badge": "",
            "is_featured": False,
            "is_trending": True,
            "rating": 4.5,
            "reviews_count": 22100,
            "short_description": "Fix your posture in 30 days. Invisible under clothes. Comfortable all day.",
            "description": "Transform your posture in just 30 days. Our Posture Corrector Brace is invisible under clothes and comfortable enough to wear all day. Recommended by chiropractors. Over 22,000 people improved their posture!",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B07WBZ6TWF?tag=" + AMAZON_PARTNER_TAG,
            "tags": "posture,health,back pain,corrector",
            "meta_title": "Posture Corrector - Fix Posture in 30 Days | $18.99",
            "meta_description": "Fix your posture in 30 days. Invisible, comfortable. 22,000+ reviews. Order now!",
        },
        {
            "name": "Cocktail Maker Machine",
            "slug": "cocktail-maker-machine",
            "price": 69.99,
            "old_price": 129.99,
            "category": "home-kitchen",
            "badge": "WOW PRICE",
            "is_featured": True,
            "is_trending": False,
            "rating": 4.6,
            "reviews_count": 3400,
            "short_description": "Make 200+ cocktails in seconds. Just add pods. Bartender quality.",
            "description": "Become your own bartender with our Cocktail Maker Machine. Over 200 cocktail recipes at the touch of a button. Just insert a cocktail pod and press start. Perfect for parties, date nights, or everyday luxury.",
            "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B09DLKHN5M?tag=" + AMAZON_PARTNER_TAG,
            "tags": "cocktail,bar,kitchen,party",
            "meta_title": "Cocktail Maker Machine - 200+ Drinks | $69.99",
            "meta_description": "Make 200+ cocktails in seconds. Bartender quality at home. Order now!",
        },
        {
            "name": "Magnetic Phone Mount for Car",
            "slug": "magnetic-phone-mount-car",
            "price": 12.99,
            "old_price": 24.99,
            "category": "electronics",
            "badge": "",
            "is_featured": False,
            "is_trending": True,
            "rating": 4.7,
            "reviews_count": 18700,
            "short_description": "One-hand operation. 360 rotation. Strongest magnets.",
            "description": "The strongest magnetic phone mount for your car. One-hand operation, 360-degree rotation, and dashboard/windshield mounting. Works with all phones including heavy Pro Max models. Over 18,700 happy drivers!",
            "image_url": "https://images.unsplash.com/photo-1611262588024-d25581e285f1?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B0BRLR5Y4Y?tag=" + AMAZON_PARTNER_TAG,
            "tags": "phone mount,car,magnetic,holder",
            "meta_title": "Magnetic Car Phone Mount - Strongest Hold | $12.99",
            "meta_description": "Strongest magnetic phone mount for car. One-hand use. 18,700+ reviews. Order now!",
        },
        {
            "name": "Weighted Blanket 15lbs",
            "slug": "weighted-blanket-15lbs",
            "price": 34.99,
            "old_price": 64.99,
            "category": "home-kitchen",
            "badge": "BEST SLEEP",
            "is_featured": True,
            "is_trending": False,
            "rating": 4.8,
            "reviews_count": 12500,
            "short_description": "Deep pressure therapy for better sleep. Glass bead filling. Soft cover.",
            "description": "Sleep better tonight with our Weighted Blanket. Medical-grade deep pressure therapy helps reduce anxiety and improve sleep quality. Glass bead filling distributes weight evenly. Removable, machine-washable cover.",
            "image_url": "https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B07GBYP81Q?tag=" + AMAZON_PARTNER_TAG,
            "tags": "blanket,sleep,anxiety,comfort",
            "meta_title": "Weighted Blanket 15lbs - Better Sleep | $34.99",
            "meta_description": "Weighted blanket for better sleep. Deep pressure therapy. 12,500+ reviews. Order now!",
        },
        {
            "name": "Mini Projector HD 1080p",
            "slug": "mini-projector-hd",
            "price": 59.99,
            "old_price": 119.99,
            "category": "electronics",
            "badge": "HOT ITEM",
            "is_featured": True,
            "is_trending": True,
            "rating": 4.6,
            "reviews_count": 7200,
            "short_description": "Home theater in your pocket. 1080p HD. WiFi & Bluetooth.",
            "description": "Turn any wall into a cinema with our Mini Projector. Crystal clear 1080p HD, built-in WiFi and Bluetooth, and 200-inch projection. Connect to your phone, laptop, or gaming console.",
            "image_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B0BQ285F98?tag=" + AMAZON_PARTNER_TAG,
            "tags": "projector,movie,home theater,portable",
            "meta_title": "Mini Projector 1080p HD - Home Cinema | $59.99",
            "meta_description": "1080p HD mini projector. WiFi, Bluetooth, 200 inch. Order now!",
        },
        {
            "name": "Car Air Purifier HEPA",
            "slug": "car-air-purifier-hepa",
            "price": 22.99,
            "old_price": 39.99,
            "category": "automotive",
            "badge": "",
            "is_featured": False,
            "is_trending": True,
            "rating": 4.5,
            "reviews_count": 5600,
            "short_description": "Eliminates 99.97% of allergens. USB powered. Silent operation.",
            "description": "Breathe clean air in your car with our HEPA Air Purifier. Eliminates 99.97% of dust, pollen, and odors. USB powered - works in any car. Silent operation won't distract you while driving.",
            "image_url": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B0CW87XJ2C?tag=" + AMAZON_PARTNER_TAG,
            "tags": "air purifier,car,health,hepa",
            "meta_title": "Car Air Purifier HEPA - Clean Air | $22.99",
            "meta_description": "HEPA car air purifier. 99.97% allergen removal. USB powered. Order now!",
        },
        {
            "name": "Selfie Ring Light with Tripod",
            "slug": "selfie-ring-light-tripod",
            "price": 16.99,
            "old_price": 32.99,
            "category": "electronics",
            "badge": "",
            "is_featured": False,
            "is_trending": True,
            "rating": 4.6,
            "reviews_count": 28900,
            "short_description": "Perfect lighting for every video. 3 modes. Phone holder included.",
            "description": "Look your best in every video with our Selfie Ring Light. 3 lighting modes, adjustable brightness, and sturdy tripod stand. Perfect for TikTok, Instagram, Zoom calls, and makeup.",
            "image_url": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=500",
            "affiliate_url": "https://www.amazon.com/dp/B093GMX12V?tag=" + AMAZON_PARTNER_TAG,
            "tags": "ring light,tripod,selfie,tiktok",
            "meta_title": "Ring Light with Tripod - Perfect Video Lighting | $16.99",
            "meta_description": "Ring light with tripod for perfect videos. 28,900+ reviews. Order now!",
        },
    ]
    for p in products:
        product = Product(
            name=p["name"],
            slug=p["slug"],
            description=p["description"],
            short_description=p["short_description"],
            price=p["price"],
            old_price=p.get("old_price"),
            image_url=p["image_url"],
            affiliate_url=p.get("affiliate_url", ""),
            category=p["category"],
            rating=p["rating"],
            reviews_count=p["reviews_count"],
            badge=p.get("badge", ""),
            is_featured=p.get("is_featured", False),
            is_trending=p.get("is_trending", False),
            tags=p.get("tags", ""),
            meta_title=p.get("meta_title", ""),
            meta_description=p.get("meta_description", ""),
        )
        db.session.add(product)
    db.session.commit()


def log_click(product_id):
    try:
        click = ClickLog(
            product_id=product_id,
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:300],
            referrer=str(request.referrer)[:500] if request.referrer else "",
            device="mobile" if "mobile" in str(request.user_agent).lower() else "desktop",
        )
        db.session.add(click)
        product = Product.query.get(product_id)
        if product:
            product.click_count = (product.click_count or 0) + 1
        db.session.commit()
    except Exception:
        db.session.rollback()


def track_visitor():
    try:
        ip = request.remote_addr
        visitor = Visitor.query.filter_by(ip_address=ip).first()
        if visitor:
            visitor.pages_viewed = (visitor.pages_viewed or 0) + 1
            visitor.last_visit = datetime.utcnow()
        else:
            visitor = Visitor(ip_address=ip, country="Unknown")
            db.session.add(visitor)
        db.session.commit()
    except Exception:
        db.session.rollback()


@app.before_request
def before_request():
    track_visitor()


@app.context_processor
def inject_globals():
    return {
        "store_name": STORE_NAME,
        "store_tagline": STORE_TAGLINE,
        "categories": CATEGORIES,
        "now": datetime.utcnow(),
    }


@app.route("/")
def home():
    featured = Product.query.filter_by(is_featured=True).limit(8).all()
    trending = Product.query.filter_by(is_trending=True).limit(8).all()
    return render_template("home.html", featured=featured, trending=trending)


@app.route("/products")
def products():
    category = request.args.get("category", "")
    sort = request.args.get("sort", "newest")
    q = request.args.get("q", "")

    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if q:
        query = query.filter(
            Product.name.ilike(f"%{q}%") |
            Product.description.ilike(f"%{q}%") |
            Product.tags.ilike(f"%{q}%")
        )

    if sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    elif sort == "popular":
        query = query.order_by(Product.sales_count.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products_list = query.all()
    return render_template(
        "products.html",
        products=products_list,
        current_category=category,
        current_sort=sort,
        search_query=q,
    )


@app.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    related = (
        Product.query
        .filter_by(category=product.category)
        .filter(Product.id != product.id)
        .limit(4)
        .all()
    )
    return render_template("product_detail.html", product=product, related=related)


@app.route("/buy/<int:product_id>")
def buy(product_id):
    product = Product.query.get_or_404(product_id)
    log_click(product_id)
    if product.affiliate_url:
        return redirect(product.affiliate_url)
    flash("Affiliate link not available yet.", "info")
    return redirect(url_for("product_detail", slug=product.slug))


@app.route("/search")
def search():
    q = request.args.get("q", "")
    if not q:
        return redirect(url_for("products"))
    results = Product.query.filter(
        Product.name.ilike(f"%{q}%") |
        Product.description.ilike(f"%{q}%") |
        Product.tags.ilike(f"%{q}%")
    ).all()
    return render_template(
        "products.html",
        products=results,
        search_query=q,
        current_category="",
        current_sort="newest",
    )


@app.route("/category/<slug>")
def category(slug):
    return redirect(url_for("products", category=slug))


@app.route("/trending")
def trending():
    products_list = (
        Product.query
        .filter_by(is_trending=True)
        .order_by(Product.sales_count.desc())
        .all()
    )
    return render_template(
        "products.html",
        products=products_list,
        current_category="trending",
        current_sort="popular",
    )


@app.route("/deals")
def deals():
    products_list = (
        Product.query
        .filter(Product.old_price.isnot(None))
        .filter(Product.old_price > Product.price)
        .all()
    )
    return render_template(
        "products.html",
        products=products_list,
        current_category="deals",
        current_sort="newest",
    )


@app.route("/api/products")
def api_products():
    products_list = Product.query.all()
    return jsonify([p.to_dict() for p in products_list])


@app.route("/api/stats")
def api_stats():
    stats = {
        "total_products": Product.query.count(),
        "total_clicks": db.session.query(db.func.sum(Product.click_count)).scalar() or 0,
        "total_sales": db.session.query(db.func.sum(Product.sales_count)).scalar() or 0,
        "featured_count": Product.query.filter_by(is_featured=True).count(),
        "trending_count": Product.query.filter_by(is_trending=True).count(),
        "total_visitors": Visitor.query.count(),
    }
    return jsonify(stats)


@app.route("/admin")
def admin():
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    stats = {
        "total": Product.query.count(),
        "featured": Product.query.filter_by(is_featured=True).count(),
        "trending": Product.query.filter_by(is_trending=True).count(),
        "total_clicks": db.session.query(db.func.sum(Product.click_count)).scalar() or 0,
        "total_sales": db.session.query(db.func.sum(Product.sales_count)).scalar() or 0,
        "visitors": Visitor.query.count(),
    }
    return render_template("admin.html", products=products_list, stats=stats)


@app.route("/admin/add", methods=["POST"])
def admin_add():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Product name required.", "error")
        return redirect(url_for("admin"))

    slug = name.lower().replace(" ", "-").replace("'", "")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:100]

    product = Product(
        name=name,
        slug=slug,
        description=request.form.get("description", ""),
        short_description=request.form.get("short_description", ""),
        price=float(request.form.get("price", 0)),
        old_price=float(request.form.get("old_price", 0)) or None,
        image_url=request.form.get("image_url", ""),
        affiliate_url=request.form.get("affiliate_url", ""),
        category=request.form.get("category", "electronics"),
        rating=float(request.form.get("rating", 4.5)),
        reviews_count=int(request.form.get("reviews_count", 0)),
        badge=request.form.get("badge", ""),
        is_featured=bool(request.form.get("is_featured")),
        is_trending=bool(request.form.get("is_trending")),
        tags=request.form.get("tags", ""),
        meta_title=request.form.get("meta_title", name),
        meta_description=request.form.get("meta_description", "")[:300],
    )
    db.session.add(product)
    db.session.commit()
    flash(f"Product '{name}' added!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:product_id>", methods=["POST"])
def admin_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin"))


@app.route("/admin/ai-generate", methods=["POST"])
def admin_ai_generate():
    if not OPENAI_API_KEY:
        flash("OpenAI API key not configured.", "error")
        return redirect(url_for("admin"))
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        niche = request.form.get("niche", "electronics")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return only valid JSON array."},
                {
                    "role": "user",
                    "content": (
                        f"Generate 5 winning Amazon products for {niche}. "
                        "Each: name, price, description, short_description, "
                        "category, rating, reviews_count, badge, tags. JSON array."
                    ),
                },
            ],
            temperature=0.8,
            max_tokens=3000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        products_data = json.loads(content)
        added = 0
        for p in products_data:
            slug = p.get("name", "").lower().replace(" ", "-")[:100]
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            if slug and not Product.query.filter_by(slug=slug).first():
                product = Product(
                    name=p.get("name", ""),
                    slug=slug,
                    description=p.get("description", ""),
                    short_description=p.get("short_description", ""),
                    price=float(p.get("price", 29.99)),
                    category=p.get("category", niche),
                    rating=float(p.get("rating", 4.5)),
                    reviews_count=int(p.get("reviews_count", 1000)),
                    badge=p.get("badge", ""),
                    is_featured=True,
                    is_trending=True,
                    tags=p.get("tags", ""),
                    meta_title=p.get("name", ""),
                )
                db.session.add(product)
                added += 1
        db.session.commit()
        flash(f"AI generated {added} products!", "success")
    except Exception as e:
        flash(f"AI generation failed: {str(e)[:200]}", "error")
    return redirect(url_for("admin"))


@app.route("/sitemap.xml")
def sitemap():
    products_list = Product.query.all()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    base = request.host_url.rstrip("/")
    xml += f'  <url><loc>{base}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    xml += f'  <url><loc>{base}/products</loc><changefreq>daily</changefreq><priority>0.9</priority></url>\n'
    xml += f'  <url><loc>{base}/trending</loc><changefreq>daily</changefreq><priority>0.8</priority></url>\n'
    for p in products_list:
        xml += f'  <url><loc>{base}/product/{p.slug}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
    xml += '</urlset>'
    return xml, 200, {"Content-Type": "application/xml"}


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        seed_products()
    app.run(debug=True, port=5000, host="0.0.0.0")
