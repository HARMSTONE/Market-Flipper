import sys
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QTabWidget, QHeaderView, QLineEdit, QMessageBox, QFileDialog,
                             QListWidget, QListWidgetItem, QCheckBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from datetime import datetime, timedelta
import os
import numpy as np
from dateutil.parser import parse

os.environ['QT_PLUGIN_PATH'] = 'c:/Users/aleks/OneDrive/Документи/Albion money project/venv/Lib/site-packages/PyQt5/Qt5/plugins'

def get_file_path(filename):
    if hasattr(sys, '_MEIPASS'):  # Running as bundled EXE
        return os.path.join(sys._MEIPASS, filename)
    else:  # Running as script
        return filename

def get_file_path(filename):
    if hasattr(sys, '_MEIPASS'):  # Running as bundled EXE
        return os.path.join(sys._MEIPASS, filename)
    else:  # Running as script
        return filename

class RegionSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Server Region")
        self.setFixedSize(300, 150)
        self.setWindowIcon(QIcon("logo.png"))  # Set your icon path here
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.label = QLabel("Please select your server region:")
        layout.addWidget(self.label)
        
        self.region_combo = QComboBox()
        self.region_combo.addItems(["Europe", "America", "Asia"])
        layout.addWidget(self.region_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
    
    def get_selected_region(self):
        return self.region_combo.currentText()

class AlbionMarketAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Show region selection dialog first
        self.region_dialog = RegionSelectionDialog()
        if self.region_dialog.exec_() != QDialog.Accepted:
            sys.exit(0)
            
        self.selected_region = self.region_dialog.get_selected_region()
        self.api_base_url = self.get_api_url_for_region(self.selected_region)
        
        self.setWindowTitle(f"Market Flipper - {self.selected_region} Server")
        self.setWindowIcon(QIcon("logo.png"))  # Set your icon path here
        self.setGeometry(100, 100, 1200, 800)
        
        # Gold price history
        self.gold_history = []
        self.gold_timestamps = []
        self.media_player = QMediaPlayer()
        self.gold_sound_file = "gold_sound.mp3"
        
        # City codes (same across all regions)
        self.city_codes = {
            'Thetford': '0007',
            'Fort Sterling': '4002',
            'Lymhurst': '1002',
            'Bridgewatch': '2004',
            'Martlock': '3008',
            'Caerleon': '3005',
            'Brecilien': '5003'
        }
        
        # Resource items with proper API names
        self.resource_items = {
            'wood': ['T1_WOOD', 'T2_WOOD', 'T3_WOOD', 'T4_WOOD', 'T5_WOOD', 'T6_WOOD', 'T7_WOOD', 'T8_WOOD'],
            'planks': ['T2_PLANKS', 'T3_PLANKS', 'T4_PLANKS', 'T5_PLANKS', 'T6_PLANKS', 'T7_PLANKS', 'T8_PLANKS'],
            'ore': ['T2_ORE', 'T3_ORE', 'T4_ORE', 'T5_ORE', 'T6_ORE', 'T7_ORE', 'T8_ORE'],
            'stone': ['T1_ROCK', 'T2_ROCK', 'T3_ROCK', 'T4_ROCK', 'T5_ROCK', 'T6_ROCK', 'T7_ROCK', 'T8_ROCK'],
            'stoneblock': ['T2_STONEBLOCK', 'T3_STONEBLOCK', 'T4_STONEBLOCK', 'T5_STONEBLOCK', 'T6_STONEBLOCK', 'T7_STONEBLOCK', 'T8_STONEBLOCK'],
            'fiber': ['T2_FIBER', 'T3_FIBER', 'T4_FIBER', 'T5_FIBER', 'T6_FIBER', 'T7_FIBER', 'T8_FIBER'],
            'hide': ['T1_HIDE', 'T2_HIDE', 'T3_HIDE', 'T4_HIDE', 'T5_HIDE', 'T6_HIDE', 'T7_HIDE', 'T8_HIDE'],
            'metal': ['T2_METALBAR', 'T3_METALBAR', 'T4_METALBAR', 'T5_METALBAR', 'T6_METALBAR', 'T7_METALBAR', 'T8_METALBAR'],
            'cloth': ['T2_CLOTH', 'T3_CLOTH', 'T4_CLOTH', 'T5_CLOTH', 'T6_CLOTH', 'T7_CLOTH', 'T8_CLOTH'],
            'leather': ['T2_LEATHER', 'T3_LEATHER', 'T4_LEATHER', 'T5_LEATHER', 'T6_LEATHER', 'T7_LEATHER', 'T8_LEATHER']
        }
        
        # Human-readable names
        self.item_names = {
            'T1_WOOD': 'Tree Logs', 'T2_WOOD': 'Birch Logs', 'T3_WOOD': 'Chestnut Logs',
            'T4_WOOD': 'Pine Logs', 'T5_WOOD': 'Cedar Logs', 'T6_WOOD': 'Bloodoak Logs',
            'T7_WOOD': 'Ashenbark Logs', 'T8_WOOD': 'Whitewood Logs',
            'T2_PLANKS': 'Birch Planks', 'T3_PLANKS': 'Chestnut Planks', 'T4_PLANKS': 'Pine Planks',
            'T5_PLANKS': 'Cedar Planks', 'T6_PLANKS': 'Bloodoak Planks', 'T7_PLANKS': 'Ashenbark Planks',
            'T8_PLANKS': 'Whitewood Planks',
            'T2_ORE': 'Copper Ore', 'T3_ORE': 'Tin Ore', 'T4_ORE': 'Iron Ore',
            'T5_ORE': 'Titanium Ore', 'T6_ORE': 'Runite Ore', 'T7_ORE': 'Meteorite Ore',
            'T8_ORE': 'Adamantium Ore',
            'T1_ROCK': 'Rough Stone', 'T2_ROCK': 'Limestone', 'T3_ROCK': 'Sandstone',
            'T4_ROCK': 'Travertine', 'T5_ROCK': 'Granite', 'T6_ROCK': 'Slate',
            'T7_ROCK': 'Basalt', 'T8_ROCK': 'Marble',
            'T2_STONEBLOCK': 'Limestone Block', 'T3_STONEBLOCK': 'Sandstone Block',
            'T4_STONEBLOCK': 'Travertine Block', 'T5_STONEBLOCK': 'Granite Block',
            'T6_STONEBLOCK': 'Slate Block', 'T7_STONEBLOCK': 'Basalt Block',
            'T8_STONEBLOCK': 'Marble Block',
            'T2_FIBER': 'Cotton', 'T3_FIBER': 'Flax', 'T4_FIBER': 'Hemp',
            'T5_FIBER': 'Skyflower', 'T6_FIBER': 'Redleaf Cotton', 'T7_FIBER': 'Sunflax',
            'T8_FIBER': 'Ghost Hemp',
            'T1_HIDE': 'Scraps of Hide', 'T2_HIDE': 'Rugged Hide', 'T3_HIDE': 'Thin Hide',
            'T4_HIDE': 'Medium Hide', 'T5_HIDE': 'Heavy Hide', 'T6_HIDE': 'Robust Hide',
            'T7_HIDE': 'Thick Hide', 'T8_HIDE': 'Resilient Hide',
            'T2_METALBAR': 'Copper Bar', 'T3_METALBAR': 'Bronze Bar', 'T4_METALBAR': 'Steel Bar',
            'T5_METALBAR': 'Titanium Steel Bar', 'T6_METALBAR': 'Runite Steel Bar',
            'T7_METALBAR': 'Meteorite Steel Bar', 'T8_METALBAR': 'Adamantium Steel Bar',
            'T2_CLOTH': 'Simple Cloth', 'T3_CLOTH': 'Neat Cloth', 'T4_CLOTH': 'Fine Cloth',
            'T5_CLOTH': 'Ornate Cloth', 'T6_CLOTH': 'Lavish Cloth', 'T7_CLOTH': 'Opulent Cloth',
            'T8_CLOTH': 'Baroque Cloth',
            'T2_LEATHER': 'Stiff Leather', 'T3_LEATHER': 'Thick Leather', 'T4_LEATHER': 'Worked Leather',
            'T5_LEATHER': 'Cured Leather', 'T6_LEATHER': 'Hardened Leather',
            'T7_LEATHER': 'Reinforced Leather', 'T8_LEATHER': 'Fortified Leather'
        }
        
        self.init_ui()
        
        # Timers
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.refresh_data)
        self.resource_timer.start(300000)  # 5 minutes
        
        self.gold_timer = QTimer()
        self.gold_timer.timeout.connect(self.update_gold_data)
        self.gold_timer.start(60000)  # 1 minute
        
        # Initial data load
        self.refresh_data()
        self.update_gold_data()

    def get_api_url_for_region(self, region):
        region_urls = {
            "Europe": "https://europe.albion-online-data.com",
            "America": "https://west.albion-online-data.com",
            "Asia": "https://east.albion-online-data.com"
        }
        return region_urls.get(region, "https://europe.albion-online-data.com")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title as an image
        title_image = QLabel()
        title_image.setPixmap(QPixmap("Market_Flipper.png").scaledToHeight(180, Qt.SmoothTransformation))
        title_image.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_image)
        
        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Market Flipping Tab
        self.setup_flipping_tab()
        
        # Gold Tracker Tab
        self.setup_gold_tab()
        
        # Status bar
        self.status_bar = QLabel("Ready to fetch data...")
        main_layout.addWidget(self.status_bar)
    
    def setup_flipping_tab(self):
        flipping_tab = QWidget()
        flipping_layout = QVBoxLayout(flipping_tab)
        
        # City selection
        city_layout = QHBoxLayout()
        city_layout.addWidget(QLabel("From City:"))
        self.from_city = QComboBox()
        self.from_city.addItems(list(self.city_codes.keys()))
        city_layout.addWidget(self.from_city)
        
        city_layout.addWidget(QLabel("To City:"))
        self.to_city = QComboBox()
        self.to_city.addItems(list(self.city_codes.keys()))
        city_layout.addWidget(self.to_city)
        
        flipping_layout.addLayout(city_layout)
        
        # Tier selection with checkboxes
        tier_layout = QHBoxLayout()
        tier_layout.addWidget(QLabel("Tiers:"))
        
        self.tier_checkboxes = {}
        tier_container = QWidget()
        tier_container_layout = QHBoxLayout(tier_container)
        
        for tier in range(1, 9):
            checkbox = QCheckBox(f"T{tier}")
            checkbox.setChecked(True)
            self.tier_checkboxes[f"T{tier}"] = checkbox
            tier_container_layout.addWidget(checkbox)
        
        tier_layout.addWidget(tier_container)
        flipping_layout.addLayout(tier_layout)
        
        # Resource type filter
        resource_layout = QHBoxLayout()
        resource_layout.addWidget(QLabel("Resource Type:"))
        self.resource_type = QComboBox()
        self.resource_type.addItems(["All"] + list(self.resource_items.keys()))
        resource_layout.addWidget(self.resource_type)
        flipping_layout.addLayout(resource_layout)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.clicked.connect(self.refresh_data)
        flipping_layout.addWidget(self.refresh_btn)
        
        # Best to Flip table
        self.flip_table = QTableWidget()
        self.flip_table.setColumnCount(7)
        self.flip_table.setHorizontalHeaderLabels(["Item", "Tier", "Buy Price", "Sell Price", "From", "To", "Profit"])
        self.flip_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        flipping_layout.addWidget(self.flip_table)
        
        self.tabs.addTab(flipping_tab, "Market Flipping")
    
    def setup_gold_tab(self):
        gold_tab = QWidget()
        gold_layout = QVBoxLayout(gold_tab)
        
        # Gold controls
        controls_layout = QHBoxLayout()
        
        # Time period selection
        controls_layout.addWidget(QLabel("Time Period:"))
        self.gold_time_period = QComboBox()
        self.gold_time_period.addItems(["24 hours", "7 days", "30 days"])
        controls_layout.addWidget(self.gold_time_period)
        self.gold_time_period.currentIndexChanged.connect(self.update_gold_display)
        
        # Refresh button
        self.gold_refresh_btn = QPushButton("Refresh Gold Data")
        self.gold_refresh_btn.clicked.connect(self.update_gold_data)
        controls_layout.addWidget(self.gold_refresh_btn)
        
        # Sound selection
        self.sound_btn = QPushButton("Change Sound")
        self.sound_btn.clicked.connect(self.change_sound)
        controls_layout.addWidget(self.sound_btn)
        
        gold_layout.addLayout(controls_layout)
        
        # Gold info display
        self.gold_info = QLabel("Loading gold data...")
        self.gold_info.setFont(QFont('Arial', 12))
        gold_layout.addWidget(self.gold_info)
        
        # Gold chart
        self.gold_figure = plt.figure(figsize=(10, 5))
        self.gold_canvas = FigureCanvas(self.gold_figure)
        gold_layout.addWidget(self.gold_canvas)
        
        self.tabs.addTab(gold_tab, "Gold Tracker")
    
    def change_sound(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Sound Files (*.mp3 *.wav)")
        if file_name:
            self.gold_sound_file = file_name
            QMessageBox.information(self, "Sound Changed", f"Sound file updated to: {file_name}")
    
    def play_gold_sound(self):
        if os.path.exists(self.gold_sound_file):
            url = QUrl.fromLocalFile(self.gold_sound_file)
            content = QMediaContent(url)
            self.media_player.setMedia(content)
            self.media_player.play()
        else:
            print(f"Sound file not found: {self.gold_sound_file}")
    
    def update_gold_data(self):
        try:
            url = f"{self.api_base_url}/api/v2/stats/Gold.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    self.gold_info.setText("No gold price data available")
                    return
                    
                self.gold_history = []
                self.gold_timestamps = []
                
                for entry in data:
                    try:
                        price = float(entry['price'])
                        timestamp_str = entry['timestamp']
                        
                        try:
                            timestamp = parse(timestamp_str)
                        except:
                            timestamp = datetime.fromtimestamp(int(timestamp_str))
                        
                        self.gold_history.append(price)
                        self.gold_timestamps.append(timestamp)
                    except (KeyError, ValueError, TypeError) as e:
                        print(f"Skipping malformed gold data entry: {e}")
                
                if not self.gold_history:
                    self.gold_info.setText("No valid gold price data found")
                    return
                    
                self.update_gold_display()
            else:
                self.gold_info.setText(f"API Error: {response.status_code}")
        except Exception as e:
            self.gold_info.setText(f"Error: {str(e)}")
            print(f"Gold data error: {str(e)}")
    
    def update_gold_display(self):
        if not self.gold_history:
            self.gold_info.setText("No gold price data available")
            return
            
        current_price = self.gold_history[-1]
        time_period = self.gold_time_period.currentText()
        
        # Calculate time range
        now = datetime.now()
        if time_period == "24 hours":
            cutoff = now - timedelta(hours=24)
        elif time_period == "7 days":
            cutoff = now - timedelta(days=7)
        else:  # 30 days
            cutoff = now - timedelta(days=30)
        
        # Filter data for selected period
        filtered_prices = []
        filtered_times = []
        for price, timestamp in zip(self.gold_history, self.gold_timestamps):
            if timestamp >= cutoff:
                filtered_prices.append(price)
                filtered_times.append(timestamp)
        
        if not filtered_prices:
            self.gold_info.setText("No data available for selected period")
            return
            
        avg_price = sum(filtered_prices) / len(filtered_prices)
        price_diff = current_price - avg_price
        percent_diff = (price_diff / avg_price) * 100
        
        # Determine recommendation
        if current_price > avg_price:
            recommendation = f"SELL (current price is {percent_diff:.1f}% above average)"
            if percent_diff > 5:
                self.play_gold_sound()
        else:
            recommendation = f"BUY (current price is {abs(percent_diff):.1f}% below average)"
            if abs(percent_diff) > 5:
                self.play_gold_sound()
        
        # Update info label
        self.gold_info.setText(
            f"Current Gold Price: {current_price:,.0f} silver\n"
            f"Average Price ({time_period}): {avg_price:,.0f} silver\n"
            f"Recommendation: {recommendation}"
        )
        
        # Update chart
        self.gold_figure.clear()
        ax = self.gold_figure.add_subplot(111)
        
        # Plot price history
        ax.plot(filtered_times, filtered_prices, label='Gold Price', color='gold')
        
        # Plot average line
        ax.axhline(y=avg_price, color='red', linestyle='--', label=f'Average ({avg_price:,.0f})')
        
        # Formatting
        ax.set_title(f"Gold Price History - Last {time_period}")
        ax.set_ylabel("Price (silver)")
        ax.grid(True)
        ax.legend()
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout
        self.gold_figure.tight_layout()
        
        self.gold_canvas.draw()
    
    def get_selected_tiers(self):
        """Get list of selected tiers from checkboxes"""
        selected_tiers = []
        for tier, checkbox in self.tier_checkboxes.items():
            if checkbox.isChecked():
                selected_tiers.append(tier[1])  # Get just the number (e.g., "4" from "T4")
        return selected_tiers
    
    def refresh_data(self):
        self.status_bar.setText("Fetching data from Albion API...")
        QApplication.processEvents()
        
        try:
            items = self.get_resource_items()
            prices = self.get_market_prices(items)
            self.update_flip_table(prices)
            self.status_bar.setText("Data updated successfully")
        except Exception as e:
            self.status_bar.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {str(e)}")
    
    def get_resource_items(self):
        resource_type = self.resource_type.currentText().lower()
        selected_tiers = self.get_selected_tiers()
        
        if resource_type == 'all':
            return [item for sublist in self.resource_items.values() 
                   for item in sublist if item[1] in selected_tiers]
        return [item for item in self.resource_items.get(resource_type, []) 
               if item[1] in selected_tiers]
    
    def get_market_prices(self, items):
        prices = {}
        
        for city_name, city_code in self.city_codes.items():
            chunk_size = 50
            for i in range(0, len(items), chunk_size):
                item_chunk = items[i:i + chunk_size]
                url = f"{self.api_base_url}/api/v2/stats/prices/{','.join(item_chunk)}?locations={city_code}"
                
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for item_data in data:
                            item_id = item_data['item_id']
                            if item_id not in prices:
                                prices[item_id] = {}
                            
                            if item_data.get('quality', 1) == 1:
                                buy_price = item_data.get('buy_price_max', 0)
                                sell_price = item_data.get('sell_price_min', 0)
                                
                                if buy_price == 0:
                                    buy_price = item_data.get('buy_price_avg', 0)
                                if sell_price == 0:
                                    sell_price = item_data.get('sell_price_avg', 0)
                                
                                prices[item_id][city_name] = {
                                    'buy': buy_price,
                                    'sell': sell_price,
                                    'quality': 1
                                }
                except Exception as e:
                    print(f"Error fetching data for {city_name}: {str(e)}")
                    continue
        
        return prices
    
    def update_flip_table(self, prices):
        self.flip_table.setRowCount(0)
        
        from_city = self.from_city.currentText()
        to_city = self.to_city.currentText()
        selected_tiers = self.get_selected_tiers()
        
        if from_city == to_city:
            self.flip_table.setRowCount(1)
            self.flip_table.setItem(0, 0, QTableWidgetItem("Select different cities for flipping"))
            return
        
        rows = []
        
        for item_id, city_data in prices.items():
            tier = item_id.split('_')[0][1]
            if tier not in selected_tiers:
                continue
                
            if from_city in city_data and to_city in city_data:
                from_price = city_data[from_city]['buy']
                to_price = city_data[to_city]['sell']
                
                if from_price > 0 and to_price > 0:
                    profit = to_price - from_price
                    profit_percentage = (profit / from_price) * 100 if from_price > 0 else 0
                    
                    if profit > 0:
                        resource_name = self.item_names.get(item_id, item_id.split('_')[1].capitalize())
                        
                        rows.append({
                            'item': resource_name,
                            'tier': tier,
                            'buy': from_price,
                            'sell': to_price,
                            'from': from_city,
                            'to': to_city,
                            'profit': profit,
                            'percentage': profit_percentage
                        })
        
        rows.sort(key=lambda x: x['percentage'], reverse=True)
        
        self.flip_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.flip_table.setItem(i, 0, QTableWidgetItem(row['item']))
            self.flip_table.setItem(i, 1, QTableWidgetItem(f"T{row['tier']}"))
            self.flip_table.setItem(i, 2, QTableWidgetItem(f"{row['buy']:,}"))
            self.flip_table.setItem(i, 3, QTableWidgetItem(f"{row['sell']:,}"))
            self.flip_table.setItem(i, 4, QTableWidgetItem(row['from']))
            self.flip_table.setItem(i, 5, QTableWidgetItem(row['to']))
            self.flip_table.setItem(i, 6, QTableWidgetItem(f"{row['profit']:,} ({row['percentage']:.1f}%)"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlbionMarketAnalyzer()
    window.show()
    sys.exit(app.exec_())