import feedparser
import jinja_partials
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
jinja_partials.register_extensions(app)

feeds = {
    "teclado": {
        "title": "The Teclado Blog",
        "href": "https://blog.teclado.com/rss/",
        "show_images": True,
        "entries": {}
    },
    "deno": {
        "title": "The Deno Blog",
        "href": "https://deno.com/feed",
        "show_images": False,
        "entries": {}
    },
    "microsoft": {
        "title": "Microsoft Official",
        "href": "https://blogs.microsoft.com/feed/",
        "show_images": True,
        "entries": {}
    }
}


@app.route("/")
@app.route("/feed/<path:feed_id>")
def render_feed(feed_id: str = None):
    for id, feed_data in feeds.items():
        parsed_feed = feedparser.parse(feed_data['href'])

        for entry in parsed_feed.entries:
            if entry.link not in feed_data['entries']:
                feed_data["entries"][entry.link] = {**entry, 'read': False}

    if feed_id is None:
        feed = list(feeds.values())[0]
        feed_id = list(feeds.keys())[0]
    else:
        feed = feeds[feed_id]

    return render_template('feed.html', feed_id=feed_id, feed=feed, feeds=feeds)


@app.route("/entries/<path:feed_id>")
def render_feed_entries(feed_id: str):
    try:
        feed = feeds[feed_id]
    except KeyError:
        return "Feed not found", 404

    page = int(request.args.get("page", 0))

    return render_template(
        'partials/entry_page.html',
        feed_id=feed_id,
        entries=list(feed['entries'].values())[page * 5:page * 5 + 5],
        href=feed['href'],
        page=page,
        max_page=len(feed['entries']) // 5
    )


@app.route("/feed/<path:feed_id>/entry/<path:entry_url>")
def mark_entry_read(feed_id: str, entry_url: str):
    try:
        feed = feeds[feed_id]
    except KeyError:
        return "Feed not found", 404

    try:
        entry = feed['entries'][entry_url]
    except KeyError:
        return "Entry not found", 404

    entry['read'] = True

    return redirect(entry_url)


@app.route('/render_add_feed')
def render_add_feed():
    return render_template('partials/add_feed.html')


@app.route('/add_feed', methods=['POST'])
def add_feed():
    feed_id = request.form.get('feedID')
    url = request.form.get('url')
    title = request.form.get('title')
    show_images = request.form.get('showImages')

    feeds[feed_id] = {"title": title, "href": url, "show_images": show_images, "entries": {}}

    return redirect(url_for('render_feed', feed_id=feed_id))


if __name__ == '__main__':
    app.run()
