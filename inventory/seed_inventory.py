"""Seed script for GoldLine inventory database."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS products")

    # Create products table with price
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    # 215 products across 19 categories with varied stock levels
    products = [
        # === ORIGINAL 15 PRODUCTS (IDs 1-15) ===
        (1, "Premium Copy Paper 500 Sheets", "Paper", 8.99, 45),
        (2, "Blue Ballpoint Pens (12-pack)", "Writing", 6.49, 23),
        (3, "Heavy-Duty Stapler", "Office Equipment", 14.99, 12),
        (4, "Spiral Notebooks (3-pack)", "Paper", 9.99, 31),
        (5, "Manila File Folders (25-pack)", "Organization", 11.49, 8),
        (6, "Sticky Notes Assorted Colors (12-pack)", "Paper", 7.99, 50),
        (7, "Black Permanent Markers (6-pack)", "Writing", 8.49, 35),
        (8, "Desk Organizer - Mesh Metal", "Organization", 24.99, 6),
        (9, "Legal Pads Yellow Ruled (6-pack)", "Paper", 12.99, 28),
        (10, "Binder Clips Assorted Sizes (48-pack)", "Office Equipment", 5.99, 42),
        (11, "Whiteboard Markers (8-pack)", "Writing", 10.99, 15),
        (12, "Printer Ink Cartridge - Black", "Ink & Toner", 29.99, 3),
        (13, "Printer Ink Cartridge - Color", "Ink & Toner", 34.99, 0),
        (14, "Paper Shredder - Cross Cut", "Office Equipment", 89.99, 7),
        (15, "Ergonomic Mouse Pad with Wrist Rest", "Accessories", 16.99, 18),

        # === PAPER & NOTEBOOKS (IDs 16-35) ===
        (16, "Recycled Copy Paper 500 Sheets", "Paper & Notebooks", 9.99, 38),
        (17, "Cardstock White 250 Sheets", "Paper & Notebooks", 14.99, 22),
        (18, "Graph Paper Notebook 100 Sheets", "Paper & Notebooks", 6.49, 15),
        (19, "Color Copy Paper Assorted 500 Sheets", "Paper & Notebooks", 12.99, 0),
        (20, "Composition Notebook Wide Ruled", "Paper & Notebooks", 3.99, 44),
        (21, "Legal Size Paper 500 Sheets", "Paper & Notebooks", 11.49, 27),
        (22, "Photo Paper Glossy 50 Sheets", "Paper & Notebooks", 18.99, 7),
        (23, "Multipurpose Paper Bright White 1000 Sheets", "Paper & Notebooks", 16.99, 33),
        (24, "College Ruled Filler Paper 200 Sheets", "Paper & Notebooks", 4.99, 41),
        (25, "Waterproof Notebook All-Weather", "Paper & Notebooks", 12.49, 9),
        (26, "Tracing Paper Pad 50 Sheets", "Paper & Notebooks", 8.99, 11),
        (27, "Index Cards Ruled 3x5 (300-pack)", "Paper & Notebooks", 5.49, 52),
        (28, "Construction Paper Assorted (200-pack)", "Paper & Notebooks", 9.49, 25),
        (29, "Steno Pads Gregg Ruled (6-pack)", "Paper & Notebooks", 10.99, 18),
        (30, "Perforated Writing Pads Letter (12-pack)", "Paper & Notebooks", 24.99, 14),
        (31, "Kraft Paper Roll 30in x 100ft", "Paper & Notebooks", 19.99, 6),
        (32, "Parchment Paper Resume Quality 100 Sheets", "Paper & Notebooks", 15.49, 8),
        (33, "Dot Grid Notebook A5", "Paper & Notebooks", 11.99, 29),
        (34, "Carbonless Receipt Book (3-pack)", "Paper & Notebooks", 13.49, 16),
        (35, "Engineering Computation Pad", "Paper & Notebooks", 7.99, 12),

        # === WRITING INSTRUMENTS (IDs 36-60) ===
        (36, "Gel Pens Black (10-pack)", "Writing Instruments", 8.99, 41),
        (37, "Mechanical Pencils 0.7mm (12-pack)", "Writing Instruments", 7.49, 33),
        (38, "Fine Tip Permanent Markers (4-pack)", "Writing Instruments", 6.99, 19),
        (39, "Highlighters Assorted (6-pack)", "Writing Instruments", 5.49, 52),
        (40, "Rollerball Pens Blue (3-pack)", "Writing Instruments", 12.99, 3),
        (41, "Dry Erase Markers Fine Tip (8-pack)", "Writing Instruments", 9.49, 0),
        (42, "No. 2 Pencils Pre-Sharpened (24-pack)", "Writing Instruments", 4.99, 60),
        (43, "Felt Tip Pens Assorted Colors (12-pack)", "Writing Instruments", 11.49, 22),
        (44, "Retractable Gel Pens Blue (8-pack)", "Writing Instruments", 9.99, 37),
        (45, "Chisel Tip Highlighters Yellow (12-pack)", "Writing Instruments", 7.99, 48),
        (46, "Fine Point Pens Black (20-pack)", "Writing Instruments", 10.49, 26),
        (47, "Colored Pencils Artist Quality (24-pack)", "Writing Instruments", 14.99, 13),
        (48, "Erasable Gel Pens (8-pack)", "Writing Instruments", 11.99, 17),
        (49, "Calligraphy Pens Assorted Tips (6-pack)", "Writing Instruments", 16.49, 4),
        (50, "Pencil Sharpener Electric", "Writing Instruments", 24.99, 10),
        (51, "Grease Pencils White (12-pack)", "Writing Instruments", 8.49, 14),
        (52, "Ballpoint Pens Medium Point Black (60-pack)", "Writing Instruments", 15.99, 35),
        (53, "Paint Markers Oil-Based (8-pack)", "Writing Instruments", 13.49, 7),
        (54, "Correction Pens (6-pack)", "Writing Instruments", 6.49, 21),
        (55, "Fountain Pen with Ink Cartridges", "Writing Instruments", 19.99, 2),
        (56, "Erasable Highlighters (5-pack)", "Writing Instruments", 7.49, 0),
        (57, "Metallic Gel Pens (10-pack)", "Writing Instruments", 8.99, 24),
        (58, "Woodcase Pencils HB (72-pack)", "Writing Instruments", 12.49, 43),
        (59, "Dual Tip Markers Fine/Broad (12-pack)", "Writing Instruments", 17.99, 5),
        (60, "Retractable Ballpoint Pens Red (12-pack)", "Writing Instruments", 5.99, 30),

        # === DESK SUPPLIES (IDs 61-80) ===
        (61, "Desktop Tape Dispenser with Tape Roll", "Desk Supplies", 8.99, 34),
        (62, "Standard Staples 5000-Count", "Desk Supplies", 3.49, 55),
        (63, "Scissors 8-Inch Stainless Steel", "Desk Supplies", 6.99, 28),
        (64, "Paper Clips Jumbo (100-pack)", "Desk Supplies", 2.99, 47),
        (65, "Rubber Bands Assorted Sizes 1lb Box", "Desk Supplies", 4.49, 39),
        (66, "Pushpins Clear (100-pack)", "Desk Supplies", 3.99, 32),
        (67, "Letter Opener Stainless Steel", "Desk Supplies", 5.49, 11),
        (68, "3-Hole Punch Heavy Duty", "Desk Supplies", 19.99, 9),
        (69, "Glue Sticks (12-pack)", "Desk Supplies", 6.49, 42),
        (70, "Correction Tape (10-pack)", "Desk Supplies", 12.99, 20),
        (71, "Desk Tape Refills 6-Roll Pack", "Desk Supplies", 9.99, 26),
        (72, "Mini Stapler with Staples", "Desk Supplies", 4.99, 0),
        (73, "Magnifying Glass Desktop", "Desk Supplies", 14.49, 3),
        (74, "Pencil Cup Holder Mesh", "Desk Supplies", 5.99, 22),
        (75, "Staple Remover Jaw Style", "Desk Supplies", 1.99, 51),
        (76, "Double-Sided Tape (3-pack)", "Desk Supplies", 7.49, 18),
        (77, "Paper Fasteners Brass (100-pack)", "Desk Supplies", 4.49, 15),
        (78, "Electric Stapler 20-Sheet Capacity", "Desk Supplies", 29.99, 4),
        (79, "Self-Inking Date Stamp", "Desk Supplies", 12.49, 8),
        (80, "Craft Knife with Replacement Blades", "Desk Supplies", 7.99, 13),

        # === FILING & ORGANIZATION (IDs 81-100) ===
        (81, "Hanging File Folders Letter (25-pack)", "Filing & Organization", 12.99, 24),
        (82, "3-Ring Binder 1-Inch White", "Filing & Organization", 4.49, 38),
        (83, "3-Ring Binder 2-Inch Black", "Filing & Organization", 7.99, 19),
        (84, "3-Ring Binder 3-Inch Heavy Duty", "Filing & Organization", 11.49, 10),
        (85, "Sheet Protectors Clear (100-pack)", "Filing & Organization", 9.99, 31),
        (86, "Tab Dividers 8-Tab (6 sets)", "Filing & Organization", 8.49, 25),
        (87, "Expanding File Accordion 13-Pocket", "Filing & Organization", 14.99, 7),
        (88, "Label Maker Handheld", "Filing & Organization", 29.99, 6),
        (89, "File Storage Box with Lid (4-pack)", "Filing & Organization", 19.99, 15),
        (90, "Magazine File Holders (6-pack)", "Filing & Organization", 16.49, 11),
        (91, "Plastic File Folders Assorted (12-pack)", "Filing & Organization", 7.49, 33),
        (92, "Hanging File Folder Tabs (50-pack)", "Filing & Organization", 3.99, 44),
        (93, "Desktop File Sorter 5-Section", "Filing & Organization", 18.99, 8),
        (94, "Clipboard Storage Case", "Filing & Organization", 22.49, 2),
        (95, "Index Dividers A-Z", "Filing & Organization", 5.99, 27),
        (96, "Document Holder Easel", "Filing & Organization", 12.49, 0),
        (97, "Portable File Box with Handle", "Filing & Organization", 15.99, 14),
        (98, "Binder Spine Inserts (25-pack)", "Filing & Organization", 3.49, 36),
        (99, "Color-Coded Labels (500-pack)", "Filing & Organization", 11.99, 20),
        (100, "Wall-Mount File Organizer 3-Tier", "Filing & Organization", 24.99, 5),

        # === INK & TONER (IDs 101-115) ===
        (101, "HP 61 Black Ink Cartridge", "Ink & Toner", 24.99, 4),
        (102, "HP 61 Tri-Color Ink Cartridge", "Ink & Toner", 29.99, 2),
        (103, "Brother TN-760 High Yield Toner Black", "Ink & Toner", 54.99, 8),
        (104, "Canon PG-245 Black Ink Cartridge", "Ink & Toner", 19.99, 0),
        (105, "Epson 502 Black Ink Bottle", "Ink & Toner", 13.49, 6),
        (106, "HP 206A Cyan Toner Cartridge", "Ink & Toner", 69.99, 1),
        (107, "Brother LC3013 Magenta Ink", "Ink & Toner", 17.99, 5),
        (108, "HP 63 Black/Tri-Color Combo Pack", "Ink & Toner", 44.99, 3),
        (109, "Canon CLI-281 Photo Value Pack", "Ink & Toner", 49.99, 0),
        (110, "Epson 212XL High Yield Black", "Ink & Toner", 27.49, 7),
        (111, "HP 410X High Yield Black Toner", "Ink & Toner", 79.99, 2),
        (112, "Brother TN-227 Yellow Toner", "Ink & Toner", 59.99, 1),
        (113, "Canon PG-275/CL-276 Combo Pack", "Ink & Toner", 34.49, 9),
        (114, "HP 952 Black Ink Cartridge", "Ink & Toner", 32.99, 4),
        (115, "Epson 302XL High Yield Cyan", "Ink & Toner", 22.49, 0),

        # === TECHNOLOGY & ACCESSORIES (IDs 116-140) ===
        (116, "USB 3.0 Flash Drive 64GB", "Technology & Accessories", 9.99, 35),
        (117, "Wireless Ergonomic Mouse", "Technology & Accessories", 29.99, 14),
        (118, "USB-C Hub 7-in-1", "Technology & Accessories", 34.99, 11),
        (119, "1080p Webcam with Microphone", "Technology & Accessories", 49.99, 6),
        (120, "Surge Protector 6-Outlet Power Strip", "Technology & Accessories", 19.99, 28),
        (121, "HDMI Cable 6ft", "Technology & Accessories", 8.49, 45),
        (122, "Bluetooth Keyboard Full Size", "Technology & Accessories", 39.99, 0),
        (123, "USB-A to USB-C Cable 3ft (2-pack)", "Technology & Accessories", 11.99, 40),
        (124, "Wireless Presenter Clicker", "Technology & Accessories", 24.99, 9),
        (125, "Laptop Stand Adjustable Aluminum", "Technology & Accessories", 44.99, 7),
        (126, "USB Desktop Microphone", "Technology & Accessories", 34.49, 3),
        (127, "Ethernet Cable Cat6 25ft", "Technology & Accessories", 12.99, 23),
        (128, "Wireless Headset with Noise Cancelling", "Technology & Accessories", 79.99, 4),
        (129, "Monitor Privacy Screen 24-Inch", "Technology & Accessories", 39.49, 5),
        (130, "USB 3.0 External Card Reader", "Technology & Accessories", 14.99, 16),
        (131, "Power Bank 10000mAh", "Technology & Accessories", 24.49, 21),
        (132, "Cable Management Kit (50-piece)", "Technology & Accessories", 16.99, 18),
        (133, "Bluetooth Mouse Compact Travel", "Technology & Accessories", 19.49, 26),
        (134, "USB Charging Station 6-Port", "Technology & Accessories", 29.49, 10),
        (135, "Screen Cleaning Kit with Microfiber Cloth", "Technology & Accessories", 8.99, 37),
        (136, "Webcam Cover Slide (3-pack)", "Technology & Accessories", 6.99, 53),
        (137, "UPS Battery Backup 600VA", "Technology & Accessories", 69.99, 0),
        (138, "Wireless Keyboard and Mouse Combo", "Technology & Accessories", 44.49, 12),
        (139, "USB Flash Drive 128GB", "Technology & Accessories", 16.49, 19),
        (140, "DisplayPort to HDMI Adapter", "Technology & Accessories", 11.49, 31),

        # === BOARDS & PRESENTATION (IDs 141-152) ===
        (141, "Magnetic Whiteboard 24x36", "Boards & Presentation", 34.99, 8),
        (142, "Cork Bulletin Board 18x24", "Boards & Presentation", 19.99, 14),
        (143, "Easel Pad 27x34 (50 Sheets)", "Boards & Presentation", 24.99, 11),
        (144, "Laser Pointer Presentation Green", "Boards & Presentation", 14.99, 20),
        (145, "Magnetic Whiteboard 48x36", "Boards & Presentation", 69.99, 3),
        (146, "Dry Erase Board Eraser Magnetic", "Boards & Presentation", 5.49, 32),
        (147, "Tripod Easel Adjustable", "Boards & Presentation", 39.99, 5),
        (148, "Whiteboard Cleaning Spray 8oz", "Boards & Presentation", 6.99, 25),
        (149, "Portable Presentation Easel Folding", "Boards & Presentation", 89.99, 0),
        (150, "Fabric Bulletin Board 36x24", "Boards & Presentation", 29.49, 7),
        (151, "Glass Dry Erase Board 24x18", "Boards & Presentation", 49.99, 2),
        (152, "Poster Board White (10-pack)", "Boards & Presentation", 9.99, 36),

        # === MAILING & SHIPPING (IDs 153-167) ===
        (153, "No. 10 Security Envelopes (500-pack)", "Mailing & Shipping", 24.99, 22),
        (154, "Manila Envelopes 9x12 (100-pack)", "Mailing & Shipping", 19.99, 17),
        (155, "Bubble Mailers 6x10 (25-pack)", "Mailing & Shipping", 14.99, 29),
        (156, "Shipping Tape Clear 6-Roll Pack", "Mailing & Shipping", 16.49, 34),
        (157, "Padded Envelopes 10x13 (12-pack)", "Mailing & Shipping", 11.99, 13),
        (158, "Packing Peanuts 14 Cubic Feet", "Mailing & Shipping", 29.99, 4),
        (159, "Tape Gun Dispenser Heavy Duty", "Mailing & Shipping", 18.99, 10),
        (160, "Mailing Labels White 1x2.6 (750-pack)", "Mailing & Shipping", 12.49, 26),
        (161, "Poly Mailers 10x13 (100-pack)", "Mailing & Shipping", 17.99, 0),
        (162, "Bubble Wrap Roll 12in x 175ft", "Mailing & Shipping", 24.49, 8),
        (163, "Corrugated Shipping Boxes 12x12x12 (25-pack)", "Mailing & Shipping", 34.99, 6),
        (164, "Self-Seal White Envelopes No. 10 (100-pack)", "Mailing & Shipping", 8.99, 43),
        (165, "Priority Mail Stickers (Roll of 500)", "Mailing & Shipping", 4.99, 15),
        (166, "Packing Tape Fragile Printed (6-pack)", "Mailing & Shipping", 13.99, 19),
        (167, "Stretch Wrap 18in x 1500ft", "Mailing & Shipping", 21.99, 3),

        # === CLEANING & BREAKROOM (IDs 168-187) ===
        (168, "Disinfecting Wipes Canister (75-count)", "Cleaning & Breakroom", 5.99, 40),
        (169, "Hand Sanitizer 8oz Pump Bottle", "Cleaning & Breakroom", 4.49, 55),
        (170, "Coffee K-Cups Medium Roast (48-count)", "Cleaning & Breakroom", 24.99, 18),
        (171, "Sugar Packets (400-count)", "Cleaning & Breakroom", 8.99, 30),
        (172, "Creamer Cups French Vanilla (50-count)", "Cleaning & Breakroom", 11.49, 22),
        (173, "Paper Cups 8oz (100-pack)", "Cleaning & Breakroom", 6.99, 37),
        (174, "Paper Plates 9-Inch (150-pack)", "Cleaning & Breakroom", 9.99, 24),
        (175, "Napkins White Lunch (500-pack)", "Cleaning & Breakroom", 7.49, 33),
        (176, "Trash Bags 13-Gallon Tall Kitchen (100-count)", "Cleaning & Breakroom", 14.99, 21),
        (177, "Air Freshener Spray Linen Scent", "Cleaning & Breakroom", 4.99, 16),
        (178, "Dish Soap Liquid 24oz", "Cleaning & Breakroom", 3.49, 28),
        (179, "Paper Towel Rolls (12-pack)", "Cleaning & Breakroom", 19.99, 15),
        (180, "Coffee Ground Colombian 12oz Bag", "Cleaning & Breakroom", 9.49, 0),
        (181, "Stirrers Wooden 5.5in (1000-pack)", "Cleaning & Breakroom", 5.49, 45),
        (182, "Microfiber Cleaning Cloths (12-pack)", "Cleaning & Breakroom", 8.49, 27),
        (183, "Foam Cups Insulated 12oz (50-pack)", "Cleaning & Breakroom", 7.99, 0),
        (184, "Multi-Surface Cleaner Spray 32oz", "Cleaning & Breakroom", 4.99, 31),
        (185, "Hot Chocolate K-Cups (24-count)", "Cleaning & Breakroom", 14.49, 9),
        (186, "Plastic Utensils Combo Pack (300-count)", "Cleaning & Breakroom", 12.99, 11),
        (187, "Bottled Water 16.9oz (24-pack)", "Cleaning & Breakroom", 6.49, 42),

        # === FURNITURE & ERGONOMICS (IDs 188-202) ===
        (188, "LED Desk Lamp Adjustable Brightness", "Furniture & Ergonomics", 29.99, 17),
        (189, "Monitor Riser Wood with Storage", "Furniture & Ergonomics", 24.99, 9),
        (190, "Mesh Office Chair with Lumbar Support", "Furniture & Ergonomics", 249.99, 5),
        (191, "Standing Desk Converter 32-Inch", "Furniture & Ergonomics", 199.99, 3),
        (192, "2-Drawer Filing Cabinet Steel", "Furniture & Ergonomics", 89.99, 12),
        (193, "Desk Pad Leather 24x14", "Furniture & Ergonomics", 19.99, 31),
        (194, "Ergonomic Footrest Adjustable", "Furniture & Ergonomics", 34.99, 8),
        (195, "Keyboard Tray Under-Desk", "Furniture & Ergonomics", 44.99, 4),
        (196, "Bookends Heavy Duty Metal (Pair)", "Furniture & Ergonomics", 14.99, 23),
        (197, "Monitor Arm Single Adjustable", "Furniture & Ergonomics", 39.99, 6),
        (198, "Cable Management Tray Under-Desk", "Furniture & Ergonomics", 17.49, 20),
        (199, "Anti-Fatigue Standing Mat 20x30", "Furniture & Ergonomics", 29.49, 15),
        (200, "Coat Rack Freestanding Metal", "Furniture & Ergonomics", 49.99, 0),
        (201, "Desktop Whiteboard Calendar 18x12", "Furniture & Ergonomics", 22.99, 10),
        (202, "Task Chair Armless Fabric", "Furniture & Ergonomics", 149.99, 2),

        # === BADGES & ID (IDs 203-207) ===
        (203, "Badge Holders Vertical (25-pack)", "Badges & ID", 8.99, 30),
        (204, "Lanyards with Clip (25-pack)", "Badges & ID", 11.49, 22),
        (205, "Badge Reels Retractable (5-pack)", "Badges & ID", 7.99, 17),
        (206, "ID Card Sleeves Clear (50-pack)", "Badges & ID", 5.49, 35),
        (207, "Visitor Badge Stickers (200-pack)", "Badges & ID", 14.99, 13),

        # === LAMINATING (IDs 208-211) ===
        (208, "Laminating Pouches Letter Size (100-pack)", "Laminating", 19.99, 16),
        (209, "Laminating Pouches Legal Size (50-pack)", "Laminating", 17.49, 10),
        (210, "Thermal Laminator Machine 9-Inch", "Laminating", 34.99, 7),
        (211, "Self-Seal Laminating Pouches (25-pack)", "Laminating", 14.49, 12),

        # === CALENDARS & PLANNERS (IDs 212-215) ===
        (212, "Desk Calendar Monthly Stand-Up", "Calendars & Planners", 8.99, 25),
        (213, "Wall Calendar 12-Month Large", "Calendars & Planners", 12.99, 19),
        (214, "Weekly Planner Hardcover", "Calendars & Planners", 16.99, 14),
        (215, "Monthly Planner with Tabs", "Calendars & Planners", 14.49, 21),
    ]

    cursor.executemany(
        "INSERT INTO products (id, name, category, price, quantity) VALUES (?, ?, ?, ?, ?)",
        products
    )

    conn.commit()
    conn.close()
    print(f"Seeded {len(products)} products into {DB_PATH}")


if __name__ == "__main__":
    seed()
