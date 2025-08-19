#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Chat Final Working Viewer
Упрощенная и гарантированно рабочая версия с экспортом изображений
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
import threading
import math

# Импорт для создания изображений
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class TelegramChatFinalWorking:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Chat Final Working Viewer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#17212b')
        
        # Данные чата
        self.chat_data = None
        self.messages = []
        self.filtered_messages = []
        self.current_chat_name = ""
        self.search_query = ""
        
        # Настройки виртуализации
        self.messages_per_page = 20
        self.current_page = 0
        self.total_pages = 0
        
        # Цвета Telegram Web
        self.colors = {
            'bg': '#17212b',
            'chat_bg': '#0e1621',
            'my_message': '#2b5278',
            'other_message': '#182533',
            'text': '#ffffff',
            'time': '#708499',
            'name': '#5bb3f0',
            'service': '#708499',
            'button': '#5bb3f0',
            'search_bg': '#232e3c',
            'date_bg': '#232e3c',
            'border': '#2f3b4c'
        }
        
        # Настройки Canvas
        self.canvas_width = 800
        self.canvas_height = 500
        self.message_padding = 20
        self.bubble_padding = 12
        self.max_bubble_width = 400
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setup_top_panel()
        self.setup_search_panel()
        self.setup_canvas_area()
        self.setup_navigation_panel()
        self.setup_bottom_panel()
        
    def setup_top_panel(self):
        """Настройка верхней панели"""
        top_frame = tk.Frame(self.root, bg=self.colors['bg'], height=60)
        top_frame.pack(fill='x', padx=10, pady=5)
        top_frame.pack_propagate(False)
        
        # Кнопка загрузки
        load_btn = tk.Button(
            top_frame, 
            text="📁 Загрузить JSON",
            command=self.load_chat_file,
            bg=self.colors['button'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            cursor='hand2'
        )
        load_btn.pack(side='left', pady=15)
        
        # Название чата
        self.chat_title = tk.Label(
            top_frame,
            text="Выберите файл чата",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold')
        )
        self.chat_title.pack(side='left', padx=20, pady=15)
        
        # Кнопка экспорта в изображение
        export_btn = tk.Button(
            top_frame,
            text="🖼️ Экспорт в PNG(50/50)",
            command=self.export_to_image_simple,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            cursor='hand2',
            state='disabled'
        )
        export_btn.pack(side='right', pady=15)
        self.export_btn = export_btn
        
    def setup_search_panel(self):
        """Настройка панели поиска"""
        search_frame = tk.Frame(self.root, bg=self.colors['bg'], height=40)
        search_frame.pack(fill='x', padx=10, pady=(0, 5))
        search_frame.pack_propagate(False)
        
        tk.Label(
            search_frame,
            text="🔍",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack(side='left', padx=(0, 5), pady=10)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.colors['search_bg'],
            fg=self.colors['text'],
            font=('Arial', 10),
            relief='flat',
            bd=1,
            insertbackground=self.colors['text']
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), pady=10, ipady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        clear_btn = tk.Button(
            search_frame,
            text="✕",
            command=self.clear_search,
            bg=self.colors['other_message'],
            fg=self.colors['text'],
            font=('Arial', 9),
            relief='flat',
            width=3,
            cursor='hand2'
        )
        clear_btn.pack(side='right', pady=10)
        
    def setup_canvas_area(self):
        """Настройка Canvas для отображения чата"""
        canvas_frame = tk.Frame(self.root, bg=self.colors['chat_bg'], relief='solid', bd=1)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.colors['chat_bg'],
            highlightthickness=0,
            scrollregion=(0, 0, 0, 2000)
        )
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        
    def setup_navigation_panel(self):
        """Настройка панели навигации"""
        nav_frame = tk.Frame(self.root, bg=self.colors['bg'], height=40)
        nav_frame.pack(fill='x', padx=10, pady=5)
        nav_frame.pack_propagate(False)
        
        self.prev_btn = tk.Button(
            nav_frame,
            text="◀ Предыдущие",
            command=self.prev_page,
            bg=self.colors['button'],
            fg='white',
            font=('Arial', 9),
            relief='flat',
            padx=15,
            cursor='hand2',
            state='disabled'
        )
        self.prev_btn.pack(side='left', pady=5)
        
        self.page_label = tk.Label(
            nav_frame,
            text="Страница 0 из 0",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10)
        )
        self.page_label.pack(side='left', padx=20, pady=5)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="Следующие ▶",
            command=self.next_page,
            bg=self.colors['button'],
            fg='white',
            font=('Arial', 9),
            relief='flat',
            padx=15,
            cursor='hand2',
            state='disabled'
        )
        self.next_btn.pack(side='left', pady=5)
        
        last_btn = tk.Button(
            nav_frame,
            text="⏭ К последним",
            command=self.go_to_last,
            bg=self.colors['other_message'],
            fg=self.colors['text'],
            font=('Arial', 9),
            relief='flat',
            padx=15,
            cursor='hand2',
            state='disabled'
        )
        last_btn.pack(side='right', pady=5)
        self.last_btn = last_btn
        
    def setup_bottom_panel(self):
        """Настройка нижней панели"""
        bottom_frame = tk.Frame(self.root, bg=self.colors['bg'], height=30)
        bottom_frame.pack(fill='x', padx=10, pady=5)
        bottom_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            bottom_frame,
            text="Готов к загрузке чата",
            bg=self.colors['bg'],
            fg=self.colors['time'],
            font=('Arial', 9)
        )
        self.stats_label.pack(side='left', pady=5)
        
    def on_canvas_configure(self, event):
        """Обработка изменения размера Canvas"""
        self.canvas_width = event.width
        self.redraw_canvas()
        
    def on_mousewheel(self, event):
        """Обработка прокрутки колесом мыши"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def load_chat_file(self):
        """Загрузка JSON файла чата"""
        file_path = filedialog.askopenfilename(
            title="Выберите JSON файл экспорта Telegram",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.chat_title.config(text="Загрузка...")
            self.root.update()
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.chat_data = json.load(f)
                
                self.current_chat_name = self.chat_data.get('name', 'Неизвестный чат')
                self.messages = self.chat_data.get('messages', [])
                self.filtered_messages = self.messages.copy()
                
                self.chat_title.config(text=f"💬 {self.current_chat_name}")
                
                self.setup_pagination()
                self.go_to_last()
                
                self.export_btn.config(state='normal')
                self.last_btn.config(state='normal')
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\\n{str(e)}")
                self.chat_title.config(text="Ошибка загрузки")
    
    def setup_pagination(self):
        """Настройка пагинации"""
        self.total_pages = max(1, (len(self.filtered_messages) + self.messages_per_page - 1) // self.messages_per_page)
        self.current_page = 0
        self.update_navigation()
    
    def update_navigation(self):
        """Обновление кнопок навигации"""
        self.page_label.config(text=f"Страница {self.current_page + 1} из {self.total_pages}")
        
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < self.total_pages - 1 else 'disabled')
        
        self.update_stats()
    
    def prev_page(self):
        """Предыдущая страница"""
        if self.current_page > 0:
            self.current_page -= 1
            self.redraw_canvas()
    
    def next_page(self):
        """Следующая страница"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.redraw_canvas()
    
    def go_to_last(self):
        """Переход к последним сообщениям"""
        self.current_page = self.total_pages - 1
        self.redraw_canvas()
    
    def redraw_canvas(self):
        """Перерисовка Canvas с сообщениями"""
        if not self.filtered_messages:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas_width // 2, 100,
                text="Сообщения не найдены",
                fill=self.colors['text'],
                font=('Arial', 14)
            )
            return
        
        self.canvas.delete("all")
        
        start_idx = self.current_page * self.messages_per_page
        end_idx = min(start_idx + self.messages_per_page, len(self.filtered_messages))
        page_messages = self.filtered_messages[start_idx:end_idx]
        
        y_pos = 20
        current_date = None
        
        for message in page_messages:
            msg_date = self.get_message_date(message)
            if msg_date != current_date:
                y_pos = self.draw_date_separator(msg_date, y_pos)
                current_date = msg_date
            
            if message.get('type') == 'service':
                y_pos = self.draw_service_message(message, y_pos)
            else:
                y_pos = self.draw_message_bubble(message, y_pos)
        
        self.canvas.configure(scrollregion=(0, 0, 0, y_pos + 50))
        self.update_navigation()
        self.canvas.yview_moveto(1.0)
    
    def draw_date_separator(self, date_str, y_pos):
        """Рисование разделителя дня"""
        text_width = len(date_str) * 8
        bg_width = text_width + 20
        bg_height = 25
        
        x_center = self.canvas_width // 2
        bg_x1 = x_center - bg_width // 2
        bg_x2 = x_center + bg_width // 2
        
        self.canvas.create_rectangle(
            bg_x1, y_pos, bg_x2, y_pos + bg_height,
            fill=self.colors['date_bg'],
            outline="",
            tags="date_separator"
        )
        
        self.canvas.create_text(
            x_center, y_pos + bg_height // 2,
            text=date_str,
            fill=self.colors['time'],
            font=('Arial', 10),
            tags="date_separator"
        )
        
        return y_pos + bg_height + 15
    
    def draw_service_message(self, message, y_pos):
        """Рисование служебного сообщения"""
        action = message.get('action', '')
        actor = message.get('actor', '')
        time_str = self.format_time(message.get('date', ''))
        
        service_text = f"{actor} {self.get_action_text(action)} • {time_str}"
        x_center = self.canvas_width // 2
        
        self.canvas.create_text(
            x_center, y_pos,
            text=service_text,
            fill=self.colors['service'],
            font=('Arial', 10),
            tags="service"
        )
        
        return y_pos + 25
    
    def draw_message_bubble(self, message, y_pos):
        """Рисование пузырька сообщения"""
        from_user = message.get('from', '')
        from_id = message.get('from_id', '')
        text = message.get('text', '')
        time_str = self.format_time(message.get('date', ''))
        
        is_my_message = 'user6582117962' in from_id
        
        if isinstance(text, list):
            full_text = ""
            for item in text:
                if isinstance(item, dict):
                    full_text += item.get('text', '')
                else:
                    full_text += str(item)
            text = full_text
        
        if not text.strip():
            text = self.get_media_text(message)
        
        if len(text) > 200:
            text = text[:200] + "..."
        
        lines = self.wrap_text(text, 40)
        
        line_height = 18
        text_height = len(lines) * line_height
        name_height = 20 if (not is_my_message and from_user) else 0
        time_height = 15
        
        bubble_width = min(self.max_bubble_width, max(200, max(len(line) * 8 for line in lines) + 20))
        bubble_height = name_height + text_height + time_height + self.bubble_padding * 2
        
        if is_my_message:
            bubble_x = self.canvas_width - bubble_width - self.message_padding
            bubble_color = self.colors['my_message']
        else:
            bubble_x = self.message_padding
            bubble_color = self.colors['other_message']
        
        self.draw_rounded_rectangle(
            bubble_x, y_pos, bubble_x + bubble_width, y_pos + bubble_height,
            radius=18, fill=bubble_color, tags="message_bubble"
        )
        
        if is_my_message:
            self.canvas.create_polygon(
                bubble_x + bubble_width, y_pos + bubble_height - 15,
                bubble_x + bubble_width + 8, y_pos + bubble_height - 8,
                bubble_x + bubble_width, y_pos + bubble_height - 5,
                fill=bubble_color, outline="", tags="message_bubble"
            )
        else:
            self.canvas.create_polygon(
                bubble_x, y_pos + bubble_height - 15,
                bubble_x - 8, y_pos + bubble_height - 8,
                bubble_x, y_pos + bubble_height - 5,
                fill=bubble_color, outline="", tags="message_bubble"
            )
        
        text_x = bubble_x + self.bubble_padding
        text_y = y_pos + self.bubble_padding
        
        if not is_my_message and from_user:
            self.canvas.create_text(
                text_x, text_y,
                text=from_user,
                fill=self.colors['name'],
                font=('Arial', 10, 'bold'),
                anchor='nw',
                tags="message_text"
            )
            text_y += name_height
        
        for line in lines:
            self.canvas.create_text(
                text_x, text_y,
                text=line,
                fill=self.colors['text'],
                font=('Arial', 11),
                anchor='nw',
                tags="message_text"
            )
            text_y += line_height
        
        time_x = bubble_x + bubble_width - self.bubble_padding - len(time_str) * 6
        time_y = y_pos + bubble_height - time_height - 5
        
        self.canvas.create_text(
            time_x, time_y,
            text=time_str,
            fill=self.colors['time'],
            font=('Arial', 9),
            anchor='nw',
            tags="message_time"
        )
        
        return y_pos + bubble_height + 10
    
    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Рисование скругленного прямоугольника на Canvas"""
        points = []
        
        for i in range(0, 90, 10):
            x = x1 + radius - radius * math.cos(math.radians(i))
            y = y1 + radius - radius * math.sin(math.radians(i))
            points.extend([x, y])
        
        for i in range(90, 180, 10):
            x = x2 - radius - radius * math.cos(math.radians(i))
            y = y1 + radius - radius * math.sin(math.radians(i))
            points.extend([x, y])
        
        for i in range(180, 270, 10):
            x = x2 - radius - radius * math.cos(math.radians(i))
            y = y2 - radius - radius * math.sin(math.radians(i))
            points.extend([x, y])
        
        for i in range(270, 360, 10):
            x = x1 + radius - radius * math.cos(math.radians(i))
            y = y2 - radius - radius * math.sin(math.radians(i))
            points.extend([x, y])
        
        return self.canvas.create_polygon(points, smooth=True, **kwargs)
    
    def wrap_text(self, text, max_chars):
        """Разбивка текста на строки"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [""]
    
    def get_media_text(self, message):
        """Получение текста для медиафайлов"""
        if 'photo' in message:
            return "📷 Фото"
        elif message.get('media_type') == 'sticker':
            emoji = message.get('sticker_emoji', '🎭')
            return f"{emoji} Стикер"
        elif message.get('media_type') == 'video_message':
            return "🎥 Видеосообщение"
        elif message.get('media_type') == 'video_file':
            return "🎥 Видео"
        elif message.get('media_type') == 'audio_file':
            return f"🎵 {message.get('file_name', 'Аудиофайл')}"
        elif message.get('media_type') == 'voice_message':
            return "🎤 Голосовое сообщение"
        elif message.get('media_type') == 'animation':
            return "🎬 GIF анимация"
        elif 'file' in message:
            return f"📎 {message.get('file_name', 'Файл')}"
        else:
            return "Сообщение"
    
    def on_search(self, event=None):
        """Обработка поиска"""
        query = self.search_var.get().lower().strip()
        self.search_query = query
        
        if not query:
            self.filtered_messages = self.messages.copy()
        else:
            self.filtered_messages = []
            for msg in self.messages:
                text = msg.get('text', '')
                if isinstance(text, list):
                    full_text = ""
                    for item in text:
                        if isinstance(item, dict):
                            full_text += item.get('text', '')
                        else:
                            full_text += str(item)
                    text = full_text
                
                from_user = msg.get('from', '')
                
                if (query in text.lower() or 
                    query in from_user.lower() or
                    query in msg.get('file_name', '').lower()):
                    self.filtered_messages.append(msg)
        
        self.setup_pagination()
        self.go_to_last()
    
    def clear_search(self):
        """Очистка поиска"""
        self.search_var.set("")
        self.on_search()
    
    def update_stats(self):
        """Обновление статистики"""
        if not self.messages:
            self.stats_label.config(text="Готов к загрузке чата")
            return
        
        total_messages = len(self.messages)
        filtered_count = len(self.filtered_messages)
        
        users = set()
        for msg in self.messages:
            if 'from' in msg:
                users.add(msg.get('from'))
        
        stats_text = f"Всего сообщений: {total_messages}"
        if self.search_query:
            stats_text += f" | Найдено: {filtered_count}"
        stats_text += f" | Участников: {len(users)}"
        
        start_idx = self.current_page * self.messages_per_page + 1
        end_idx = min((self.current_page + 1) * self.messages_per_page, filtered_count)
        stats_text += f" | Показано: {start_idx}-{end_idx}"
        
        self.stats_label.config(text=stats_text)
    
    def format_time(self, date_str):
        """Форматирование времени"""
        try:
            dt = datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', ''))
            return dt.strftime('%H:%M')
        except:
            return "00:00"
    
    def get_message_date(self, message):
        """Получение даты сообщения"""
        try:
            date_str = message.get('date', '')
            dt = datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', ''))
            return dt.strftime('%d.%m.%Y')
        except:
            return "Неизвестная дата"
    
    def get_action_text(self, action):
        """Получение текста для служебного действия"""
        actions = {
            'joined_telegram': 'присоединился к Telegram',
            'left_chat': 'покинул чат',
            'joined_chat': 'присоединился к чату',
            'created_chat': 'создал чат'
        }
        return actions.get(action, action)
    
    def export_to_image_simple(self):
        """Упрощенный экспорт в изображение"""
        if not self.messages:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        if not PIL_AVAILABLE:
            messagebox.showerror("Ошибка", "Библиотека Pillow не установлена.\\nУстановите её командой: pip install pillow")
            return
        
        # Простой диалог выбора количества сообщений
        dialog = SimpleExportDialog(self.root, len(self.filtered_messages))
        if not dialog.result:
            return
        
        max_messages = dialog.result
        
        # Выбор пути сохранения - ЧЕТКИЙ И ПРОСТОЙ
        default_filename = f"{self.current_chat_name.replace(' ', '_')}_chat_{max_messages}msg.png"
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение чата",
            defaultextension=".png",
            filetypes=[("PNG изображения", "*.png"), ("Все файлы", "*.*")],
            initialfilename=default_filename
        )
        
        if not file_path:
            messagebox.showinfo("Отмена", "Экспорт отменен")
            return
        
        # Показываем простой прогресс
        progress_window = SimpleProgressWindow(self.root)
        
        def create_image():
            try:
                progress_window.update_status("Подготовка данных...")
                
                # Берем последние сообщения
                messages_to_export = self.filtered_messages[-max_messages:] if len(self.filtered_messages) > max_messages else self.filtered_messages
                
                progress_window.update_status("Создание изображения...")
                
                # Создаем простое изображение
                self.create_simple_image(messages_to_export, file_path, progress_window)
                
                progress_window.close()
                
                # Показываем результат
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path) / 1024  # в КБ
                    messagebox.showinfo(
                        "Успех!", 
                        f"✅ Изображение создано!\\n\\n"
                        f"📁 Файл: {file_path}\\n"
                        f"📊 Сообщений: {len(messages_to_export)}\\n"
                        f"💾 Размер: {file_size:.1f} КБ"
                    )
                else:
                    messagebox.showerror("Ошибка", "Файл не был создан")
                    
            except Exception as e:
                progress_window.close()
                messagebox.showerror("Ошибка", f"Не удалось создать изображение:\\n{str(e)}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=create_image)
        thread.daemon = True
        thread.start()
    
    def create_simple_image(self, messages, output_path, progress_window):
        """Создание простого изображения чата"""
        # Настройки
        width = 1200
        background_color = (23, 33, 43)  # #17212b
        text_color = (255, 255, 255)
        my_bubble_color = (43, 82, 120)  # #2b5278
        other_bubble_color = (24, 37, 51)  # #182533
        
        # Примерная высота
        estimated_height = len(messages) * 80 + 200
        height = min(estimated_height, 8000)  # Ограничиваем высоту
        
        # Создаем изображение
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Пытаемся загрузить шрифт
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        progress_window.update_status("Рисование заголовка...")
        
        # Заголовок
        title = f"💬 {self.current_chat_name}"
        title_bbox = draw.textbbox((0, 0), title, font=font_bold)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 30), title, fill=text_color, font=font_bold)
        
        subtitle = f"Последние {len(messages)} сообщений"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        draw.text((subtitle_x, 60), subtitle, fill=(112, 132, 153), font=font_small)
        
        # Рисуем сообщения
        y_pos = 120
        current_date = None
        
        for i, message in enumerate(messages):
            if y_pos > height - 100:
                break
            
            # Обновляем прогресс
            if i % 10 == 0:
                progress = int((i / len(messages)) * 100)
                progress_window.update_status(f"Обработано {i+1}/{len(messages)} сообщений ({progress}%)")
            
            # Разделитель дня
            msg_date = self.get_message_date(message)
            if msg_date != current_date:
                y_pos = self.draw_simple_date_separator(draw, msg_date, y_pos, width, font_small)
                current_date = msg_date
            
            # Сообщение
            if message.get('type') == 'service':
                y_pos = self.draw_simple_service_message(draw, message, y_pos, width, font_small)
            else:
                y_pos = self.draw_simple_message(draw, message, y_pos, width, font, font_small, my_bubble_color, other_bubble_color, text_color)
        
        progress_window.update_status("Сохранение файла...")
        
        # Обрезаем до нужной высоты
        final_height = min(y_pos + 50, height)
        img = img.crop((0, 0, width, final_height))
        
        # Сохраняем
        img.save(output_path, 'PNG', quality=100)
    
    def draw_simple_date_separator(self, draw, date_str, y_pos, width, font):
        """Простой разделитель даты"""
        bbox = draw.textbbox((0, 0), date_str, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        bg_width = text_width + 20
        bg_height = text_height + 10
        bg_x = (width - bg_width) // 2
        
        # Фон
        draw.rectangle([bg_x, y_pos, bg_x + bg_width, y_pos + bg_height], fill=(35, 46, 60))
        
        # Текст
        text_x = bg_x + 10
        text_y = y_pos + 5
        draw.text((text_x, text_y), date_str, fill=(112, 132, 153), font=font)
        
        return y_pos + bg_height + 20
    
    def draw_simple_service_message(self, draw, message, y_pos, width, font):
        """Простое служебное сообщение"""
        action = message.get('action', '')
        actor = message.get('actor', '')
        time_str = self.format_time(message.get('date', ''))
        
        service_text = f"{actor} {self.get_action_text(action)} • {time_str}"
        
        bbox = draw.textbbox((0, 0), service_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        
        draw.text((text_x, y_pos), service_text, fill=(112, 132, 153), font=font)
        
        return y_pos + 30
    
    def draw_simple_message(self, draw, message, y_pos, width, font, font_small, my_color, other_color, text_color):
        """Простое сообщение"""
        from_user = message.get('from', '')
        from_id = message.get('from_id', '')
        text = message.get('text', '')
        time_str = self.format_time(message.get('date', ''))
        
        is_my_message = 'user6582117962' in from_id
        
        # Обработка текста
        if isinstance(text, list):
            full_text = ""
            for item in text:
                if isinstance(item, dict):
                    full_text += item.get('text', '')
                else:
                    full_text += str(item)
            text = full_text
        
        if not text.strip():
            text = self.get_media_text(message)
        
        # Ограничиваем длину
        if len(text) > 300:
            text = text[:300] + "..."
        
        # Разбиваем на строки
        max_chars = 50
        lines = []
        words = text.split()
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        if not lines:
            lines = [""]
        
        # Размеры пузырька
        line_height = 20
        padding = 15
        max_line_width = max(len(line) for line in lines) * 8
        bubble_width = min(500, max(200, max_line_width + padding * 2))
        
        name_height = 20 if (not is_my_message and from_user) else 0
        text_height = len(lines) * line_height
        time_height = 15
        bubble_height = name_height + text_height + time_height + padding * 2
        
        # Позиция пузырька
        if is_my_message:
            bubble_x = width - bubble_width - 50
            bubble_color = my_color
        else:
            bubble_x = 50
            bubble_color = other_color
        
        # Рисуем пузырек (простой прямоугольник)
        draw.rectangle([bubble_x, y_pos, bubble_x + bubble_width, y_pos + bubble_height], fill=bubble_color)
        
        # Текст внутри пузырька
        text_x = bubble_x + padding
        text_y = y_pos + padding
        
        # Имя отправителя
        if not is_my_message and from_user:
            draw.text((text_x, text_y), from_user, fill=(91, 179, 240), font=font)
            text_y += name_height
        
        # Текст сообщения
        for line in lines:
            draw.text((text_x, text_y), line, fill=text_color, font=font)
            text_y += line_height
        
        # Время
        time_x = bubble_x + bubble_width - padding - len(time_str) * 6
        time_y = y_pos + bubble_height - time_height - 5
        draw.text((time_x, time_y), time_str, fill=(112, 132, 153), font=font_small)
        
        return y_pos + bubble_height + 15

class SimpleExportDialog:
    def __init__(self, parent, max_messages):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Экспорт в изображение")
        self.dialog.geometry("400x250")
        self.dialog.configure(bg='#17212b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        x = parent.winfo_rootx() + 50
        y = parent.winfo_rooty() + 50
        self.dialog.geometry(f"+{x}+{y}")
        
        # Заголовок
        tk.Label(
            self.dialog,
            text="🖼️ Экспорт в изображение",
            bg='#17212b',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=20)
        
        tk.Label(
            self.dialog,
            text="Выберите количество сообщений:",
            bg='#17212b',
            fg='white',
            font=('Arial', 11)
        ).pack(pady=(0, 15))
        
        # Варианты
        self.var = tk.IntVar(value=min(50, max_messages))
        
        options = [
            (20, "20 сообщений (быстро)"),
            (50, "50 сообщений (оптимально)"),
            (100, "100 сообщений (медленно)"),
            (min(200, max_messages), f"Максимум ({min(200, max_messages)} сообщений)")
        ]
        
        for value, text in options:
            if value <= max_messages:
                tk.Radiobutton(
                    self.dialog,
                    text=text,
                    variable=self.var,
                    value=value,
                    bg='#17212b',
                    fg='white',
                    selectcolor='#2b5278',
                    font=('Arial', 10),
                    activebackground='#17212b',
                    activeforeground='white'
                ).pack(anchor='w', padx=50, pady=3)
        
        # Кнопки
        btn_frame = tk.Frame(self.dialog, bg='#17212b')
        btn_frame.pack(pady=30)
        
        tk.Button(
            btn_frame,
            text="✅ Создать",
            command=self.ok_clicked,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            btn_frame,
            text="❌ Отмена",
            command=self.cancel_clicked,
            bg='#708499',
            fg='white',
            font=('Arial', 10),
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    def ok_clicked(self):
        self.result = self.var.get()
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

class SimpleProgressWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Создание изображения")
        self.window.geometry("350x120")
        self.window.configure(bg='#17212b')
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем
        x = parent.winfo_rootx() + 100
        y = parent.winfo_rooty() + 100
        self.window.geometry(f"+{x}+{y}")
        
        tk.Label(
            self.window,
            text="🖼️ Создание изображения чата",
            bg='#17212b',
            fg='white',
            font=('Arial', 12, 'bold')
        ).pack(pady=20)
        
        self.status_label = tk.Label(
            self.window,
            text="Подготовка...",
            bg='#17212b',
            fg='#708499',
            font=('Arial', 10)
        )
        self.status_label.pack(pady=(0, 20))
        
        # Простой прогресс-бар
        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill='x')
        self.progress.start()
    
    def update_status(self, message):
        """Обновление статуса"""
        self.status_label.config(text=message)
        self.window.update()
    
    def close(self):
        self.window.destroy()

def main():
    root = tk.Tk()
    app = TelegramChatFinalWorking(root)
    
    # Центрирование окна
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()

