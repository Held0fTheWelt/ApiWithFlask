from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route('/api/books', methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        # Handle the GET request
        # For now, we'll return a static list
        books = [
            {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
            {"id": 2, "title": "1984", "author": "George Orwell"}
        ]
        return jsonify(books)

    elif request.method == 'POST':
        # Handle the POST request
        # For now, we'll just return the data the user sent
        # Later, we'll add code to save the new book in our data storage
        new_book = request.get_json()
        return jsonify(new_book), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)