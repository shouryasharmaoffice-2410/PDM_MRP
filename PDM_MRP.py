#!/usr/bin/env python3
"""
ULTRA-SIMPLE CAD/MRP SYSTEM
Just 3 files: parts_database.csv + bom_database.csv + this script
"""

import pandas as pd
from datetime import datetime, timedelta
import os

# ==================== CONFIGURATION ====================
PARTS_FILE = 'parts_database.csv'
BOM_FILE = 'bom_database.csv'
REPORTS_FOLDER = 'reports'

# ==================== LOAD DATA ====================

def load_parts():
    """Load parts from CSV"""
    if not os.path.exists(PARTS_FILE):
        print("❌ parts_database.csv not found!")
        return None
    return pd.read_csv(PARTS_FILE)

def load_bom():
    """Load BOM from CSV"""
    if not os.path.exists(BOM_FILE):
        print("❌ bom_database.csv not found!")
        return None
    return pd.read_csv(BOM_FILE)

# ==================== MRP CALCULATION ====================

def explode_bom(parent_part, production_qty=1, parts_df=None, bom_df=None, visited=None):
    """Recursively get all child parts needed"""
    if parts_df is None:
        parts_df = load_parts()
    if bom_df is None:
        bom_df = load_bom()
    if visited is None:
        visited = {}
    
    # Get direct children
    children = bom_df[bom_df['parent_part_number'] == parent_part]
    
    for _, child in children.iterrows():
        child_part = child['child_part_number']
        qty_needed = child['quantity'] * production_qty
        
        # Add to total
        if child_part in visited:
            visited[child_part] += qty_needed
        else:
            visited[child_part] = qty_needed
        
        # Recursively explode child's BOM
        explode_bom(child_part, qty_needed, parts_df, bom_df, visited)
    
    return visited

def calculate_mrp(parent_part_number, production_qty=1):
    """Calculate material requirements"""
    parts_df = load_parts()
    bom_df = load_bom()
    
    if parts_df is None or bom_df is None:
        return None
    
    # Check if parent exists
    parent = parts_df[parts_df['part_number'] == parent_part_number]
    if parent.empty:
        print(f"❌ Part {parent_part_number} not found!")
        return None
    
    parent = parent.iloc[0]
    
    # Explode BOM
    gross_requirements = explode_bom(parent_part_number, production_qty, parts_df, bom_df)
    
    # Calculate net requirements
    net_requirements = []
    for part_number, gross_qty in gross_requirements.items():
        part = parts_df[parts_df['part_number'] == part_number]
        
        if part.empty:
            continue
        
        part = part.iloc[0]
        on_hand = part['on_hand']
        on_order = part['on_order']
        reserved = part['reserved']
        
        available = on_hand - reserved
        net_qty = max(0, gross_qty - available - on_order)
        
        net_requirements.append({
            'Part Number': part_number,
            'Description': part['description'],
            'Type': part['type'],
            'Gross Qty Needed': gross_qty,
            'On Hand': on_hand,
            'On Order': on_order,
            'Reserved': reserved,
            'Available': available,
            'Net Qty to Order': net_qty,
            'Unit': part['unit'],
            'Supplier': part['supplier'] if pd.notna(part['supplier']) else 'N/A',
            'Lead Time (Days)': part['lead_time_days'],
            'Delivery Date': (datetime.now() + timedelta(days=int(part['lead_time_days']))).strftime('%Y-%m-%d') if net_qty > 0 else '-',
            'CAD File': part['cad_file_path'] if pd.notna(part['cad_file_path']) else 'N/A'
        })
    
    # Sort by net qty (highest first)
    net_requirements.sort(key=lambda x: x['Net Qty to Order'], reverse=True)
    
    return {
        'Parent Product': parent_part_number,
        'Production Qty': production_qty,
        'Generated At': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'Net Requirements': net_requirements,
        'Purchase Needed': any(r['Net Qty to Order'] > 0 for r in net_requirements)
    }

# ==================== REPORTS ====================

def generate_low_stock_report():
    """Generate report of items below reorder level"""
    parts_df = load_parts()
    
    if parts_df is None:
        return None
    
    low_stock = parts_df[parts_df['on_hand'] < parts_df['reorder_level']].copy()
    
    if low_stock.empty:
        print("✓ No items below reorder level!")
        return None
    
    low_stock['Shortage'] = low_stock['reorder_level'] - low_stock['on_hand']
    low_stock = low_stock.sort_values('Shortage', ascending=False)
    
    return low_stock

def export_to_excel(data, filename):
    """Export data to Excel"""
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    filepath = os.path.join(REPORTS_FOLDER, filename)
    
    if isinstance(data, dict):
        df = pd.DataFrame(data['Net Requirements'])
    else:
        df = data
    
    df.to_excel(filepath, index=False)
    print(f"✓ Exported to: {filepath}")
    return filepath

# ==================== MAIN MENU ====================

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🏭 ULTRA-SIMPLE CAD/MRP SYSTEM")
        print("="*60)
        print("1. Calculate MRP for a product")
        print("2. View all parts")
        print("3. Show low stock items")
        print("4. Export all reports to Excel")
        print("5. Exit")
        print("="*60)
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            # Calculate MRP
            part = input("Enter parent part number (e.g., PROD-00789-A): ").strip()
            qty = input("Production quantity (default 1): ").strip() or '1'
            
            result = calculate_mrp(part, int(qty))
            
            if result:
                print("\n" + "="*60)
                print(f"MRP for {result['Parent Product']} x {result['Production Qty']}")
                print(f"Generated: {result['Generated At']}")
                print("="*60)
                
                if result['Net Requirements']:
                    print(f"\n{'Part Number':<20} {'Description':<25} {'On Hand':<10} {'Need to Order':<15}")
                    print("-"*70)
                    
                    for req in result['Net Requirements']:
                        if req['Net Qty to Order'] > 0:
                            print(f"{req['Part Number']:<20} {req['Description']:<25} {req['On Hand']:<10} {req['Net Qty to Order']:<15}")
                    
                    print("\n✓ Items needing purchase:")
                    for req in result['Net Requirements']:
                        if req['Net Qty to Order'] > 0:
                            print(f"  • {req['Part Number']}: {req['Net Qty to Order']} {req['Unit']} (Supplier: {req['Supplier']}, Lead: {req['Lead Time (Days)']} days)")
                    
                    # Export to Excel
                    export = input("\nExport to Excel? (y/n): ").strip().lower()
                    if export == 'y':
                        filename = f"MRP_{part}_Qty{qty}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                        export_to_excel(result, filename)
                else:
                    print("No materials needed — you have enough stock!")

        elif choice == '2':
            # View all parts
            parts_df = load_parts()
            if parts_df is not None:
                print("\n" + "="*60)
                print("ALL PARTS")
                print("="*60)
                print(parts_df[['part_number', 'description', 'type', 'on_hand', 'reorder_level', 'supplier']].to_string(index=False))
        
        elif choice == '3':
            # Show low stock
            low_stock = generate_low_stock_report()
            if low_stock is not None and not low_stock.empty:
                print("\n" + "="*60)
                print("⚠️ LOW STOCK ITEMS (Below Reorder Level)")
                print("="*60)
                print(low_stock[['part_number', 'description', 'on_hand', 'reorder_level', 'Shortage', 'supplier']].to_string(index=False))
                
                export = input("\nExport to Excel? (y/n): ").strip().lower()
                if export == 'y':
                    filename = f"Low_Stock_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    export_to_excel(low_stock, filename)
        
        elif choice == '4':
            # Export all reports
            print("\nGenerating all reports...")
            
            # Low stock report
            low_stock = generate_low_stock_report()
            if low_stock is not None and not low_stock.empty:
                export_to_excel(low_stock, f"Low_Stock_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")
            
            # All parts report
            parts_df = load_parts()
            if parts_df is not None:
                export_to_excel(parts_df, f"All_Parts_{datetime.now().strftime('%Y%m%d')}.xlsx")
            
            # BOM report
            bom_df = load_bom()
            if bom_df is not None:
                export_to_excel(bom_df, f"BOM_Relationships_{datetime.now().strftime('%Y%m%d')}.xlsx")
            
            print("\n✓ All reports exported to 'reports/' folder!")
        
        elif choice == '5':
            print("\nGoodbye! 👋")
            break
        
        else:
            print("❌ Invalid choice.")

if __name__ == '__main__':
    main()