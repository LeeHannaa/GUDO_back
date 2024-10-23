from flask import Flask, jsonify, request

app = Flask(__name__)

items = [
    {"id" : 1, "name" : "apple", "price : ": 1000},
    {"id" : 2, "name" : "banana", "price : ": 2000},
    {"id" : 3, "name" : "orange", "price : ": 3000},
]

#GET /api/hello
@app.route("/api/hello")
def hello():
    return "Hello, World!"

#GET /api/items
@app.route("/api/items")
def get_items():
    return jsonify(items)

#GET /api/item/{id}
@app.route("/api/items/<int:item_id>")
def get_item(item_id):
    for item in items:
        if item["id"] == item_id:
            return jsonify(item)
    return jsonify({"message" : "Item not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)


