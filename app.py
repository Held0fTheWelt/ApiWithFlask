import logging

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from books_list import books

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def find_book_by_id(book_id):
    """Find the book with the id `book_id`.
    If there is no book with this id, return None."""
    for book in books:
        if book['id'] == book_id:
            return book
    return None


def validate_book_data(data):
    if "title" not in data or "author" not in data:
        return False
    return True


@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning("404 Not Found: %s", request.path)
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    app.logger.warning("405 Method Not Allowed: %s %s", request.method, request.path)
    return jsonify({"error": "Method Not Allowed"}), 405


@app.route('/api/books', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def handle_books():
    if request.method == 'POST':
        app.logger.info("POST request received for /api/books")
        # Get the new book data from the client
        new_book = request.get_json()
        if not validate_book_data(new_book):
            app.logger.warning("Invalid book data in POST /api/books")
            return jsonify({"error": "Invalid book data"}), 400

        # Generate a new ID for the book
        new_id = max(book['id'] for book in books) + 1
        new_book['id'] = new_id

        # Add the new book to our list
        books.append(new_book)

        app.logger.info("Created book id=%s title=%s", new_id, new_book.get("title"))
        # Return the new book data to the client
        return jsonify(new_book), 201
    else:
        app.logger.info("GET request received for /api/books")
        # Handle the GET request (with optional author filter and pagination)
        author = request.args.get('author')

        # Start with all books or only those by a given author
        if author:
            base_books = [book for book in books if book.get('author') == author]
        else:
            base_books = books

        # Pagination parameters with defaults
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        start_index = (page - 1) * limit
        end_index = start_index + limit

        paginated_books = base_books[start_index:end_index]
        return jsonify(paginated_books)


@app.route('/api/books/<int:id>', methods=['PUT'])
def handle_book(id):
    app.logger.info("PUT request received for /api/books/%s", id)
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        app.logger.warning("Book not found for PUT id=%s", id)
        return '', 404

    # Update the book with the new data
    new_data = request.get_json()
    book.update(new_data)

    app.logger.info("Updated book id=%s", id)
    # Return the updated book
    return jsonify(book)


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    app.logger.info("DELETE request received for /api/books/%s", id)
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        app.logger.warning("Book not found for DELETE id=%s", id)
        return '', 404

    # Remove the book from the list
    books.remove(book)

    app.logger.info("Deleted book id=%s title=%s", id, book.get("title"))
    # Return the deleted book
    return jsonify(book)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)