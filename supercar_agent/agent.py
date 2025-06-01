"""Simple CLI agent for supercar rental bookings."""

import json
import csv
from datetime import datetime
from pathlib import Path

INVENTORY_FILE = Path(__file__).parent / "inventory.json"
LEADS_FILE = Path(__file__).parent / "leads.csv"


def load_inventory():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def check_availability(car_id):
    inventory = load_inventory()
    for car in inventory:
        if car["id"] == car_id:
            return car.get("available", False), car
    return False, None


def calculate_total(daily_rate, start_date, end_date):
    delta = (end_date - start_date).days
    delta = max(delta, 1)
    return daily_rate * delta


def save_lead(data):
    """Append lead information to the CSV backend."""
    needs_header = not LEADS_FILE.exists() or LEADS_FILE.stat().st_size == 0
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data.keys()))
        if needs_header:
            writer.writeheader()
        writer.writerow(data)


def get_payment_link(lead_id):
    return f"https://example-payment.com/pay/{lead_id}"


def gather_input(prompt, required=True):
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    print("Hi! I can help you reserve a supercar in less than 2 minutes.")
    start_date = parse_date(gather_input("Start date (YYYY-MM-DD): "))
    end_date = parse_date(gather_input("End date (YYYY-MM-DD): "))
    location = gather_input("Pickup location: ")
    age = int(gather_input("Driver age: "))
    if age < 25:
        print("Sorry, renters must be 25 or older.")
        return
    license_no = gather_input("Driver's license number: ")
    insurance = gather_input("Insurance provider: ")
    reason = gather_input("Rental intent (hourly, event, photoshoot, etc.): ")
    inventory = load_inventory()
    print("Available cars:")
    for idx, car in enumerate(inventory, 1):
        print(f"{idx}. {car['make']} {car['model']} - ${car['daily_rate']} per day")
    choice = int(gather_input("Select a vehicle by number: "))
    if choice < 1 or choice > len(inventory):
        print("Invalid selection.")
        return
    selected_car = inventory[choice - 1]
    available, car_info = check_availability(selected_car["id"])
    if not available:
        print("Sorry, that car is not available for the selected dates.")
        return
    total_cost = calculate_total(car_info["daily_rate"], start_date, end_date)
    print(f"The {car_info['make']} {car_info['model']} is available. Total cost is ${total_cost} with a ${car_info['deposit']} deposit.")
    proceed = gather_input("Would you like to proceed with booking? (yes/no): ", required=False)
    lead = {
        "timestamp": datetime.utcnow().isoformat(),
        "start_date": start_date.date(),
        "end_date": end_date.date(),
        "location": location,
        "car_id": car_info["id"],
        "age": age,
        "license_no": license_no,
        "insurance": insurance,
        "reason": reason,
        "quote": total_cost,
        "deposit": car_info["deposit"],
        "proceed": proceed.lower() == "yes",
    }
    save_lead(lead)
    if proceed.lower() == "yes":
        link = get_payment_link(lead["timestamp"])
        print(f"I've locked your quote—complete your booking here: {link}")
    else:
        print("Thanks for inquiring! I've saved your quote and will follow up soon.")


if __name__ == "__main__":
    main()
