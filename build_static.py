import os
import re
import shutil
from datetime import datetime, timezone

import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import Product, db
from config import STORE_NAME, STORE_TAGLINE, CATEGORIES, AMAZON_PARTNER_TAG

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs")
SITE_BASE = "/shopgenius-store"


def fix_links(html, depth=0):
    prefix = "../" * depth if depth > 0 else ""

    if prefix:
        html = html.replace('href="/static/', f'href="{prefix}static/')
        html = html.replace('src="/static/', f'src="{prefix}static/')
    else:
        html = html.replace('href="/static/', 'href="static/')
        html = html.replace('src="/static/', 'src="static/')

    links = [
        ("/products", "products/index.html"),
        ("/trending", "trending/index.html"),
        ("/deals", "deals/index.html"),
        ("/", "index.html"),
    ]

    for old, new in links:
        if prefix:
            html = html.replace(f'href="{old}"', f'href="{prefix}{new}"')
            if old == "/":
                html = html.replace("href='/'", f"href='{prefix}index.html'")
        else:
            html = html.replace(f'href="{old}"', f'href="{new}"')

    html = re.sub(r'href="/category/([^"]+)"', lambda m: f'href="{prefix}category/{m.group(1)}/index.html"', html)
    html = re.sub(r'href="/product/([^"]+)"', lambda m: f'href="{prefix}product/{m.group(1)}.html"', html)
    html = re.sub(r'href="/buy/(\d+)"', lambda m: f'href="{prefix}buy/{m.group(1)}/index.html"', html)
    html = re.sub(r'href="/search\?([^"]*)"', lambda m: f'href="{prefix}products/index.html?{m.group(1)}"', html)
    html = re.sub(r'href="/admin"', 'href="#"', html)
    html = re.sub(r'href="/admin/([^"]*)"', 'href="#"', html)

    return html


def build():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for d in ["static/css", "static/js", "product", "buy", "category", "products", "trending", "deals"]:
        os.makedirs(os.path.join(OUTPUT_DIR, d), exist_ok=True)
    for cat in CATEGORIES:
        os.makedirs(os.path.join(OUTPUT_DIR, "category", cat["slug"]), exist_ok=True)

    shutil.copy2(
        os.path.join(os.path.dirname(__file__), "static", "css", "style.css"),
        os.path.join(OUTPUT_DIR, "static", "css", "style.css"),
    )
    shutil.copy2(
        os.path.join(os.path.dirname(__file__), "static", "js", "main.js"),
        os.path.join(OUTPUT_DIR, "static", "js", "main.js"),
    )

    with app.app_context():
        products = Product.query.all()
        featured = Product.query.filter_by(is_featured=True).limit(8).all()
        trending = Product.query.filter_by(is_trending=True).limit(8).all()
        deals = (
            Product.query
            .filter(Product.old_price.isnot(None))
            .filter(Product.old_price > Product.price)
            .all()
        )
        now = datetime.now(timezone.utc)

        ctx = dict(store_name=STORE_NAME, store_tagline=STORE_TAGLINE, categories=CATEGORIES, now=now)

        pages = [
            ("index.html", "home.html", dict(featured=featured, trending=trending, **ctx), 0),
            ("products/index.html", "products.html", dict(products=products, current_category="", current_sort="newest", search_query="", **ctx), 1),
            ("trending/index.html", "products.html", dict(products=[p for p in products if p.is_trending], current_category="trending", current_sort="popular", search_query="", **ctx), 1),
            ("deals/index.html", "products.html", dict(products=deals, current_category="deals", current_sort="newest", search_query="", **ctx), 1),
            ("404.html", "404.html", ctx, 0),
        ]

        for out_file, template, data, depth in pages:
            with app.test_request_context(f"/{out_file.replace('index.html', '').rstrip('/')}"):
                from flask import render_template as rt
                html = rt(template, **data)
                html = fix_links(html, depth)
                out_path = os.path.join(OUTPUT_DIR, out_file)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  Built: {out_file}")

        for p in products:
            with app.test_request_context(f"/product/{p.slug}"):
                from flask import render_template as rt
                related = [r for r in products if r.category == p.category and r.id != p.id][:4]
                html = rt("product_detail.html", product=p, related=related, **ctx)
                html = fix_links(html, 1)
                out_path = os.path.join(OUTPUT_DIR, "product", f"{p.slug}.html")
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  Built: product/{p.slug}.html")

        for p in products:
            redirect_url = p.affiliate_url or f"../product/{p.slug}.html"
            html = f'''<!DOCTYPE html>
<html><head><meta http-equiv="refresh" content="0;url={redirect_url}">
<title>Redirecting to {p.name}...</title></head>
<body><p>Redirecting to <a href="{redirect_url}">{p.name}</a>...</p></body></html>'''
            buy_dir = os.path.join(OUTPUT_DIR, "buy", str(p.id))
            os.makedirs(buy_dir, exist_ok=True)
            with open(os.path.join(buy_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html)

        for cat in CATEGORIES:
            cat_products = [p for p in products if p.category == cat["slug"]]
            if cat_products:
                with app.test_request_context(f"/category/{cat['slug']}"):
                    from flask import render_template as rt
                    html = rt("products.html", products=cat_products, current_category=cat["slug"], current_sort="newest", search_query="", **ctx)
                    html = fix_links(html, 2)
                    out_path = os.path.join(OUTPUT_DIR, "category", cat["slug"], "index.html")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(html)
                print(f"  Built: category/{cat['slug']}/index.html")

        sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        base_url = "https://mailtomindempireofficial-a11y.github.io/shopgenius-store"
        sitemap_lines.append(f'  <url><loc>{base_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
        sitemap_lines.append(f'  <url><loc>{base_url}/products/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>')
        for p in products:
            sitemap_lines.append(f'  <url><loc>{base_url}/product/{p.slug}.html</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>')
        sitemap_lines.append('</urlset>')
        with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write("\n".join(sitemap_lines))

        robots = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"
        with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(robots)

    total = sum(len(files) for _, _, files in os.walk(OUTPUT_DIR))
    print(f"\nStatic site built: {OUTPUT_DIR}")
    print(f"Total files: {total}")


if __name__ == "__main__":
    build()
