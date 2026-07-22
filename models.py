from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    short_description = db.Column(db.String(500), default="")
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default="USD")
    image_url = db.Column(db.String(500), default="")
    affiliate_url = db.Column(db.String(1000), default="")
    category = db.Column(db.String(100), default="electronics")
    rating = db.Column(db.Float, default=4.5)
    reviews_count = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(50), default="")
    is_featured = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    is_sold_out = db.Column(db.Boolean, default=False)
    sales_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    meta_title = db.Column(db.String(200), default="")
    meta_description = db.Column(db.String(300), default="")
    tags = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "slug": self.slug,
            "description": self.description, "short_description": self.short_description,
            "price": self.price, "old_price": self.old_price, "currency": self.currency,
            "image_url": self.image_url, "affiliate_url": self.affiliate_url,
            "category": self.category, "rating": self.rating, "reviews_count": self.reviews_count,
            "badge": self.badge, "is_featured": self.is_featured, "is_trending": self.is_trending,
            "is_sold_out": self.is_sold_out, "sales_count": self.sales_count,
            "click_count": self.click_count, "discount_percent": self.discount_percent(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ClickLog(db.Model):
    __tablename__ = "click_logs"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    ip_address = db.Column(db.String(50), default="")
    user_agent = db.Column(db.String(300), default="")
    referrer = db.Column(db.String(500), default="")
    country = db.Column(db.String(50), default="")
    device = db.Column(db.String(50), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    amount = db.Column(db.Float, default=0)
    commission = db.Column(db.Float, default=0)
    platform = db.Column(db.String(50), default="amazon")
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Visitor(db.Model):
    __tablename__ = "visitors"
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), unique=True)
    country = db.Column(db.String(50), default="")
    pages_viewed = db.Column(db.Integer, default=1)
    first_visit = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)
