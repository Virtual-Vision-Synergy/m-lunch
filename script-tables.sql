-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    contact_info TEXT,
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

-- Couriers
CREATE TABLE couriers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact TEXT,
    location GEOGRAPHY(POINT, 4326)
);

-- Meal types
CREATE TABLE meal_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Meals
CREATE TABLE meals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    image TEXT,
    type_id INT REFERENCES meal_types(id),
    price NUMERIC(10,2) NOT NULL
);

-- Restaurants
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150),
    location TEXT,
    image TEXT,
    geo_location GEOGRAPHY(POINT, 4326)
);

-- Delivery zones
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    area GEOGRAPHY(POLYGON, 4326)
);

-- Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Meals per order
CREATE TABLE order_meals (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    meal_id INT REFERENCES meals(id),
    added_at TIMESTAMP DEFAULT now()
);

-- Meal availability
CREATE TABLE meal_availability (
    id SERIAL PRIMARY KEY,
    meal_id INT REFERENCES meals(id),
    start_date TIMESTAMP,
    end_date TIMESTAMP
);

-- Promotions
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    meal_id INT REFERENCES meals(id),
    discount_percent INT CHECK (discount_percent BETWEEN 0 AND 100)
);

-- Order status history
CREATE TABLE order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(50),
    changed_at TIMESTAMP DEFAULT now()
);

-- Courier status history
CREATE TABLE delivery_status_history (
    id SERIAL PRIMARY KEY,
    courier_id INT REFERENCES couriers(id),
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT now()
);

-- Courier's orders
CREATE TABLE courier_orders (
    id SERIAL PRIMARY KEY,
    courier_id INT REFERENCES couriers(id),
    order_id INT REFERENCES orders(id),
    assigned_at TIMESTAMP DEFAULT now()
);

-- Meals offered by restaurant
CREATE TABLE restaurant_meals (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    meal_id INT REFERENCES meals(id)
);

-- Restaurant delivery zones
CREATE TABLE restaurant_zones (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    zone_id INT REFERENCES zones(id)
);

-- Customer preferred zones
CREATE TABLE customer_zones (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    zone_id INT REFERENCES zones(id)
);

-- Courier available zones
CREATE TABLE courier_zones (
    id SERIAL PRIMARY KEY,
    courier_id INT REFERENCES couriers(id),
    zone_id INT REFERENCES zones(id),
    available_since TIMESTAMP DEFAULT now()
);

-- Restaurant status history
CREATE TABLE restaurant_status_history (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    status VARCHAR(50),
    changed_at TIMESTAMP DEFAULT now()
);

-- Order limit per day
CREATE TABLE daily_order_limits (
    id SERIAL PRIMARY KEY,
    order_count INT CHECK (order_count >= 0),
    date DATE NOT NULL
);
