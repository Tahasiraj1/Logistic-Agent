"""
This script processes inventory and orders data, fulfilling orders based on available stock. 
It also extracts addresses from orders and saves them to a file for further processing.
"""
import json


def load_inventory():
    with open('inventory.json', 'r') as f:
        return json.load(f)

def load_orders():
    with open('orders.json', 'r') as f:
        return json.load(f)
    
def retrieve_addresses_and_demands():
    orders = load_orders()
    addresses_and_demands = []
    for order in orders:
        fullfilled = all(item['fullfilled'] for item in order['items'])
        if fullfilled:
            continue
        demands = sum(item['quantity'] for item in order['items'])
        addresses_and_demands.append((order['destination'], demands))
    
    return addresses_and_demands

def fulfill_orders(inventory_list, orders):
    inventory = {item['product_id']: item for item in inventory_list}

    for order in orders:
        print(f"\nProcessing Order {order['order_id']}...")

        for item in order['items']:
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            product = inventory.get(product_id)
            if not product:
                print(f"  ❌ Product {product_id} not found.")
                item['fullfilled'] = False 
                continue
            
            product_name = product.get('name')
            current_stock = product.get('stock')

            if current_stock < quantity:
                print(f"  ⚠️ Not enough stock for {product_name}-{product_id}. Needed: {quantity}, Available: {current_stock}")
                item['fullfilled'] = False
            else:
                inventory[product_id]['stock'] -= quantity
                print(f"  ✅ Fulfilled {quantity} of {product_name}-{product_id}. Remaining: {inventory[product_id]['stock']}")
                item['fullfilled'] = True

    # Save the updated inventory
    updated_inventory = list(inventory.values())
    with open('inventory.json', 'w') as f:
        json.dump(updated_inventory, f, indent=2)
        print("\n✔️ Inventory updated and saved.")

    # Save the updated orders
    with open('orders.json', 'w') as f:
        json.dump(orders, f, indent=2)
        print("✔️ Orders updated and saved.")

def display_inventory():
    inventory = load_inventory()
    display_items = []

    for item in inventory:
        display_items.append({
            'product_id': item['product_id'],
            'name': item['name'],
            'stock': item['stock'],
            'status': "Inventory is low" if item['stock'] < 10 else "Inventory is sufficient"
        })

    return display_items

def display_orders():
    orders = load_orders()
    display_orders = []

    for order in orders:
        for item in order['items']:
            if not item['fullfilled'] and item['quantity'] > 0:
                display_orders.append({
                    'order_id': order['order_id'],
                    'destination': order['destination'],
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'status': "Order not fulfilled"
                })

    return display_orders


# Main execution
# if __name__ == "__main__":
#     inventory = load_inventory()
#     orders = load_orders()
#     fulfill_orders(inventory, orders)


