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
    
def retrieve_inventory():
    inventory = load_inventory()
    return [item['stock'] for item in inventory]
    
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

# Main execution
# if __name__ == "__main__":
#     inventory = load_inventory()
#     orders = load_orders()
#     fulfill_orders(inventory, orders)


