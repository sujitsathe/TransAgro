from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import networkx as nx
from geopy.distance import geodesic

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(200), nullable=False)

# Create the database if it doesn't exist
with app.app_context():
    db.create_all()

# Hardcoded coordinates for some major cities
location_coords = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Nashik": (19.9975, 73.7898),
    "Nagpur": (21.1458, 79.0882),
    "Delhi": (28.7041, 77.1025)
}

# Create a graph for finding the best route
G = nx.Graph()
for city1 in location_coords:
    for city2 in location_coords:
        if city1 != city2:
            distance = geodesic(location_coords[city1], location_coords[city2]).km
            G.add_edge(city1, city2, weight=distance)

@app.route("/", methods=["GET", "POST"])
def index():
    best_route = None

    if request.method == "POST":
        name = request.form.get("name")
        destination = request.form.get("destination")

        # Save booking details to the database
        new_booking = Booking(name=name, destination=destination)
        db.session.add(new_booking)
        db.session.commit()

        # Find the best route using Dijkstra's algorithm
        start_location = "Mumbai"
        if destination in location_coords:
            best_route = nx.shortest_path(G, source=start_location, target=destination, weight="weight")

    # Fetch all previous bookings from the database
    bookings = Booking.query.all()
    return render_template("index.html", bookings=bookings, best_route=best_route)

if __name__ == "__main__":
    app.run(debug=True)
