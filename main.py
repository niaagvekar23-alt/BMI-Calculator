import customtkinter as ctk
import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


# =========================================================
# OPTIONAL PDF LIBRARY
# =========================================================

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# =========================================================
# APP SETTINGS
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("BMI+ | Smart BMI Calculator")
app.geometry("1100x760")
app.minsize(950, 680)


# =========================================================
# COLORS
# =========================================================

BG_COLOR = "#0F172A"
CARD_COLOR = "#1E293B"
CARD_DARK = "#172033"

TEXT_COLOR = "#F8FAFC"
SECONDARY_TEXT = "#94A3B8"

ACCENT_COLOR = "#3B82F6"
ACCENT_HOVER = "#2563EB"

SUCCESS_COLOR = "#22C55E"
WARNING_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"

BORDER_COLOR = "#334155"


# =========================================================
# DATABASE
# =========================================================

DATABASE_NAME = "bmi_history.db"


def setup_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT
        )
    """)

    connection.commit()
    connection.close()


setup_database()


# =========================================================
# GLOBAL DATA
# =========================================================

bmi_history = []

current_bmi = None
current_category = None
current_weight = None
current_height = None


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_all_records():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, date_time, weight, height, bmi, category
        FROM bmi_records
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return records


def save_record(weight, height, bmi, category):

    date_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bmi_records
        (date_time, weight, height, bmi, category)
        VALUES (?, ?, ?, ?, ?)
    """, (
        date_time,
        weight,
        height,
        bmi,
        category
    ))

    connection.commit()

    connection.close()

    return date_time


def delete_record(record_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM bmi_records WHERE id = ?",
        (record_id,)
    )

    connection.commit()

    connection.close()


def clear_all_records():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM bmi_records"
    )

    connection.commit()

    connection.close()


# =========================================================
# FORMAT DATE
# =========================================================

def format_date(date_time):

    try:

        return datetime.strptime(
            date_time,
            "%Y-%m-%d %H:%M:%S"
        ).strftime(
            "%d %b %Y, %I:%M %p"
        )

    except ValueError:

        return date_time


# =========================================================
# BMI CATEGORY
# =========================================================

def get_bmi_category(bmi):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obesity"


# =========================================================
# CATEGORY COLOR
# =========================================================

def get_category_color(category):

    if category == "Underweight":
        return "#60A5FA"

    elif category == "Normal":
        return SUCCESS_COLOR

    elif category == "Overweight":
        return WARNING_COLOR

    else:
        return DANGER_COLOR


# =========================================================
# LOAD HISTORY
# =========================================================

def load_history():

    global bmi_history

    records = get_all_records()

    bmi_history = records

    update_history_display()


# =========================================================
# HEIGHT FIELD FUNCTION
# =========================================================

def update_height_fields(choice):

    if choice == "cm":

        feet_entry.pack_forget()
        inches_entry.pack_forget()

        height_entry.pack(
            side="left",
            padx=(0, 10)
        )

    else:

        height_entry.pack_forget()

        feet_entry.pack(
            side="left",
            padx=(0, 5)
        )

        inches_entry.pack(
            side="left",
            padx=(0, 10)
        )


# =========================================================
# UPDATE HISTORY DISPLAY
# =========================================================

def update_history_display():

    history_text.configure(
        state="normal"
    )

    history_text.delete(
        "1.0",
        "end"
    )

    records = get_all_records()

    if not records:

        history_text.insert(
            "1.0",
            "No BMI records yet.\n\n"
            "Calculate your BMI to create history."
        )

    else:

        for index, record in enumerate(records[:20]):

            record_id, date_time, weight, height, bmi, category = record

            history_text.insert(
                "end",
                f"BMI: {bmi:.1f}  |  {category}\n"
            )

            history_text.insert(
                "end",
                f"Weight: {weight:.1f} kg  |  "
                f"Height: {height:.1f} cm\n"
            )

            history_text.insert(
                "end",
                f"{format_date(date_time)}\n"
            )

            history_text.insert(
                "end",
                "─" * 38 + "\n\n"
            )

    history_text.configure(
        state="disabled"
    )


# =========================================================
# CALCULATE BMI
# =========================================================

def calculate_bmi():

    global current_bmi
    global current_category
    global current_weight
    global current_height

    # -----------------------------------------------------
    # GET WEIGHT
    # -----------------------------------------------------

    weight_text = weight_entry.get().strip()

    if not weight_text:

        show_error(
            "Missing Input",
            "Please enter your weight."
        )

        return


    # -----------------------------------------------------
    # CONVERT WEIGHT
    # -----------------------------------------------------

    try:

        weight = float(weight_text)

    except ValueError:

        show_error(
            "Invalid Input",
            "Please enter numbers only."
        )

        return


    weight_selected_unit = weight_unit.get()


    # -----------------------------------------------------
    # LB TO KG
    # -----------------------------------------------------

    if weight_selected_unit == "lb":

        weight = weight * 0.453592


    # -----------------------------------------------------
    # WEIGHT VALIDATION
    # -----------------------------------------------------

    if weight <= 0:

        show_error(
            "Invalid Weight",
            "Weight must be greater than zero."
        )

        return


    if weight < 20 or weight > 300:

        show_error(
            "Invalid Weight",
            "Please enter a weight between 20 kg and 300 kg."
        )

        return


    # =====================================================
    # HEIGHT
    # =====================================================

    height_selected_unit = height_unit.get()


    # -----------------------------------------------------
    # CENTIMETERS
    # -----------------------------------------------------

    if height_selected_unit == "cm":

        height_text = height_entry.get().strip()

        if not height_text:

            show_error(
                "Missing Input",
                "Please enter your height."
            )

            return


        try:

            height_cm = float(height_text)

        except ValueError:

            show_error(
                "Invalid Height",
                "Please enter a valid height."
            )

            return


    # -----------------------------------------------------
    # FEET + INCHES
    # -----------------------------------------------------

    else:

        feet_text = feet_entry.get().strip()
        inches_text = inches_entry.get().strip()


        if not feet_text or not inches_text:

            show_error(
                "Missing Input",
                "Please enter both feet and inches."
            )

            return


        try:

            feet = float(feet_text)
            inches = float(inches_text)

        except ValueError:

            show_error(
                "Invalid Height",
                "Please enter valid feet and inches."
            )

            return


        if feet < 0 or inches < 0:

            show_error(
                "Invalid Height",
                "Height cannot be negative."
            )

            return


        if inches >= 12:

            show_error(
                "Invalid Inches",
                "Inches must be between 0 and 11.99."
            )

            return


        height_cm = (
            feet * 30.48
        ) + (
            inches * 2.54
        )


    # -----------------------------------------------------
    # HEIGHT VALIDATION
    # -----------------------------------------------------

    if height_cm <= 0:

        show_error(
            "Invalid Height",
            "Height must be greater than zero."
        )

        return


    if height_cm < 80 or height_cm > 250:

        show_error(
            "Invalid Height",
            "Please enter a height between 80 cm and 250 cm."
        )

        return


    # =====================================================
    # BMI CALCULATION
    # =====================================================

    height_m = height_cm / 100

    bmi = weight / (height_m ** 2)

    bmi_category = get_bmi_category(bmi)


    # =====================================================
    # SAVE CURRENT RESULT
    # =====================================================

    current_bmi = bmi
    current_category = bmi_category
    current_weight = weight
    current_height = height_cm


    # =====================================================
    # HEALTHY WEIGHT RANGE
    # =====================================================

    min_healthy_weight = (
        18.5 * (height_m ** 2)
    )

    max_healthy_weight = (
        24.9 * (height_m ** 2)
    )


    # =====================================================
    # UPDATE RESULT
    # =====================================================

    bmi_value.configure(
        text=f"{bmi:.1f}"
    )

    category.configure(
        text=bmi_category,
        text_color=get_category_color(
            bmi_category
        )
    )

    result_message.configure(
        text=(
            f"Your BMI is {bmi:.1f}\n"
            f"Category: {bmi_category}"
        )
    )

    healthy_weight.configure(
        text=(
            f"Healthy Weight\n"
            f"{min_healthy_weight:.1f} – "
            f"{max_healthy_weight:.1f} kg"
        )
    )


    # =====================================================
    # BMI PROGRESS
    # =====================================================

    progress_value = min(
        max(
            (bmi - 10) / 30,
            0
        ),
        1
    )

    bmi_progress.set(
        progress_value
    )


    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    save_record(
        weight,
        height_cm,
        bmi,
        bmi_category
    )


    # =====================================================
    # REFRESH HISTORY
    # =====================================================

    load_history()

    update_statistics()

    draw_chart()


# =========================================================
# ERROR FUNCTION
# =========================================================

def show_error(title, message):

    bmi_value.configure(
        text="--"
    )

    category.configure(
        text=title,
        text_color=DANGER_COLOR
    )

    result_message.configure(
        text=message
    )

    healthy_weight.configure(
        text="Healthy Weight: --"
    )

    bmi_progress.set(0)


# =========================================================
# RESET
# =========================================================

def reset_calculator():

    weight_entry.delete(
        0,
        "end"
    )

    height_entry.delete(
        0,
        "end"
    )

    feet_entry.delete(
        0,
        "end"
    )

    inches_entry.delete(
        0,
        "end"
    )


    weight_unit.set(
        "kg"
    )

    height_unit.set(
        "cm"
    )

    update_height_fields(
        "cm"
    )


    bmi_value.configure(
        text="--"
    )

    category.configure(
        text="Enter your details",
        text_color=SECONDARY_TEXT
    )

    result_message.configure(
        text="Your BMI result will appear here."
    )

    healthy_weight.configure(
        text="Healthy Weight: --"
    )

    bmi_progress.set(
        0
    )


# =========================================================
# DELETE SELECTED / LAST RECORD
# =========================================================

def delete_latest_record():

    records = get_all_records()

    if not records:

        messagebox.showinfo(
            "BMI History",
            "There are no records to delete."
        )

        return


    latest_record = records[0]

    record_id = latest_record[0]

    confirm = messagebox.askyesno(
        "Delete Record",
        "Delete the latest BMI record?"
    )

    if confirm:

        delete_record(
            record_id
        )

        load_history()

        update_statistics()

        draw_chart()


# =========================================================
# CLEAR HISTORY
# =========================================================

def clear_history():

    records = get_all_records()

    if not records:

        messagebox.showinfo(
            "BMI History",
            "History is already empty."
        )

        return


    confirm = messagebox.askyesno(
        "Clear History",
        "Are you sure you want to delete all BMI records?"
    )

    if confirm:

        clear_all_records()

        load_history()

        update_statistics()

        draw_chart()

        messagebox.showinfo(
            "History Cleared",
            "All BMI history has been deleted."
        )


# =========================================================
# STATISTICS
# =========================================================

def update_statistics():

    records = get_all_records()

    if not records:

        latest_stat.configure(
            text="--"
        )

        average_stat.configure(
            text="--"
        )

        highest_stat.configure(
            text="--"
        )

        lowest_stat.configure(
            text="--"
        )

        total_stat.configure(
            text="0"
        )

        return


    bmi_values = [
        record[4]
        for record in records
    ]


    latest = bmi_values[0]

    average = sum(
        bmi_values
    ) / len(
        bmi_values
    )

    highest = max(
        bmi_values
    )

    lowest = min(
        bmi_values
    )


    latest_stat.configure(
        text=f"{latest:.1f}"
    )

    average_stat.configure(
        text=f"{average:.1f}"
    )

    highest_stat.configure(
        text=f"{highest:.1f}"
    )

    lowest_stat.configure(
        text=f"{lowest:.1f}"
    )

    total_stat.configure(
        text=str(
            len(bmi_values)
        )
    )


# =========================================================
# STATISTICS WINDOW
# =========================================================

def open_statistics():

    stats_window = ctk.CTkToplevel(
        app
    )

    stats_window.title(
        "BMI+ | Statistics"
    )

    stats_window.geometry(
        "700x520"
    )

    stats_window.configure(
        fg_color=BG_COLOR
    )


    title = ctk.CTkLabel(
        stats_window,
        text="Your BMI Statistics",
        font=("Arial", 30, "bold"),
        text_color=TEXT_COLOR
    )

    title.pack(
        pady=(30, 5)
    )


    subtitle = ctk.CTkLabel(
        stats_window,
        text="Overview of your saved BMI records",
        font=("Arial", 14),
        text_color=SECONDARY_TEXT
    )

    subtitle.pack(
        pady=(0, 25)
    )


    grid = ctk.CTkFrame(
        stats_window,
        fg_color="transparent"
    )

    grid.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=10
    )


    create_stat_card(
        grid,
        "Latest BMI",
        latest_stat.cget("text"),
        0,
        0
    )

    create_stat_card(
        grid,
        "Average BMI",
        average_stat.cget("text"),
        0,
        1
    )

    create_stat_card(
        grid,
        "Highest BMI",
        highest_stat.cget("text"),
        1,
        0
    )

    create_stat_card(
        grid,
        "Lowest BMI",
        lowest_stat.cget("text"),
        1,
        1
    )

    create_stat_card(
        grid,
        "Total Records",
        total_stat.cget("text"),
        2,
        0
    )


    info = ctk.CTkLabel(
        grid,
        text=(
            "BMI is a general screening measure and "
            "does not diagnose health conditions."
        ),
        font=("Arial", 12),
        text_color=SECONDARY_TEXT
    )

    info.grid(
        row=2,
        column=1,
        padx=15,
        pady=15
    )


    for i in range(2):

        grid.grid_columnconfigure(
            i,
            weight=1
        )


# =========================================================
# CREATE STAT CARD
# =========================================================

def create_stat_card(
    parent,
    title,
    value,
    row,
    column
):

    card = ctk.CTkFrame(
        parent,
        fg_color=CARD_COLOR,
        corner_radius=15
    )

    card.grid(
        row=row,
        column=column,
        padx=10,
        pady=10,
        sticky="nsew"
    )


    title_label = ctk.CTkLabel(
        card,
        text=title,
        font=("Arial", 13),
        text_color=SECONDARY_TEXT
    )

    title_label.pack(
        pady=(20, 5)
    )


    value_label = ctk.CTkLabel(
        card,
        text=value,
        font=("Arial", 28, "bold"),
        text_color=TEXT_COLOR
    )

    value_label.pack(
        pady=(0, 20)
    )


# =========================================================
# CHART WINDOW
# =========================================================

def open_chart():

    chart_window = ctk.CTkToplevel(
        app
    )

    chart_window.title(
        "BMI+ | BMI Trend"
    )

    chart_window.geometry(
        "850x550"
    )

    chart_window.configure(
        fg_color=BG_COLOR
    )


    title = ctk.CTkLabel(
        chart_window,
        text="BMI Trend",
        font=("Arial", 28, "bold"),
        text_color=TEXT_COLOR
    )

    title.pack(
        pady=(25, 5)
    )


    subtitle = ctk.CTkLabel(
        chart_window,
        text="Your BMI records over time",
        font=("Arial", 13),
        text_color=SECONDARY_TEXT
    )

    subtitle.pack(
        pady=(0, 15)
    )


    chart_frame = ctk.CTkFrame(
        chart_window,
        fg_color=CARD_COLOR,
        corner_radius=15
    )

    chart_frame.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=20
    )


    chart_canvas = tk.Canvas(
        chart_frame,
        bg=CARD_COLOR,
        highlightthickness=0
    )

    chart_canvas.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )


    draw_chart_on_canvas(
        chart_canvas
    )


# =========================================================
# DRAW CHART
# =========================================================

def draw_chart():

    pass


def draw_chart_on_canvas(canvas_widget):

    records = get_all_records()

    canvas_widget.delete(
        "all"
    )


    if len(records) < 2:

        canvas_widget.create_text(
            400,
            180,
            text="Calculate at least 2 BMI records\nto view the trend chart.",
            fill=SECONDARY_TEXT,
            font=("Arial", 16),
            justify="center"
        )

        return


    records = list(
        reversed(
            records[:10]
        )
    )


    bmi_values = [
        record[4]
        for record in records
    ]


    width = 760
    height = 350

    left = 70
    right = 30
    top = 40
    bottom = 60


    chart_width = width - left - right
    chart_height = height - top - bottom


    min_bmi = min(
        min(bmi_values),
        10
    )

    max_bmi = max(
        max(bmi_values),
        40
    )


    if max_bmi == min_bmi:

        max_bmi += 5
        min_bmi -= 5


    # -----------------------------------------------------
    # GRID
    # -----------------------------------------------------

    for i in range(6):

        y = (
            top
            +
            (chart_height / 5) * i
        )

        value = (
            max_bmi
            -
            ((max_bmi - min_bmi) / 5) * i
        )


        canvas_widget.create_line(
            left,
            y,
            width - right,
            y,
            fill=BORDER_COLOR
        )


        canvas_widget.create_text(
            left - 10,
            y,
            text=f"{value:.0f}",
            fill=SECONDARY_TEXT,
            font=("Arial", 10),
            anchor="e"
        )


    # -----------------------------------------------------
    # POINTS
    # -----------------------------------------------------

    points = []


    for i, bmi in enumerate(bmi_values):

        if len(bmi_values) == 1:

            x = left + chart_width / 2

        else:

            x = (
                left
                +
                (
                    i
                    /
                    (len(bmi_values) - 1)
                )
                *
                chart_width
            )


        y = (
            top
            +
            (
                (max_bmi - bmi)
                /
                (max_bmi - min_bmi)
            )
            *
            chart_height
        )


        points.append(
            (x, y)
        )


    # -----------------------------------------------------
    # CONNECT POINTS
    # -----------------------------------------------------

    for i in range(
        len(points) - 1
    ):

        x1, y1 = points[i]
        x2, y2 = points[i + 1]


        canvas_widget.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=ACCENT_COLOR,
            width=3
        )


    # -----------------------------------------------------
    # DRAW POINTS
    # -----------------------------------------------------

    for i, (
        x,
        y
    ) in enumerate(points):

        canvas_widget.create_oval(
            x - 6,
            y - 6,
            x + 6,
            y + 6,
            fill=ACCENT_COLOR,
            outline=""
        )


        canvas_widget.create_text(
            x,
            y - 18,
            text=f"{bmi_values[i]:.1f}",
            fill=TEXT_COLOR,
            font=("Arial", 10, "bold")
        )


        canvas_widget.create_text(
            x,
            height - 30,
            text=str(i + 1),
            fill=SECONDARY_TEXT,
            font=("Arial", 10)
        )


    # -----------------------------------------------------
    # AXIS LABELS
    # -----------------------------------------------------

    canvas_widget.create_text(
        20,
        180,
        text="BMI",
        fill=SECONDARY_TEXT,
        font=("Arial", 11, "bold"),
        angle=90
    )


    canvas_widget.create_text(
        width / 2,
        height - 5,
        text="Recent records",
        fill=SECONDARY_TEXT,
        font=("Arial", 11)
    )


# =========================================================
# PDF REPORT
# =========================================================

def generate_pdf_report():

    if not PDF_AVAILABLE:

        messagebox.showerror(
            "PDF Support Missing",
            "Please install reportlab first:\n\n"
            "py -m pip install reportlab"
        )

        return


    records = get_all_records()

    if not records:

        messagebox.showinfo(
            "No Data",
            "Calculate your BMI first."
        )

        return


    latest = records[0]

    record_id, date_time, weight, height, bmi, category = latest


    min_healthy_weight = (
        18.5 *
        ((height / 100) ** 2)
    )

    max_healthy_weight = (
        24.9 *
        ((height / 100) ** 2)
    )


    filename = (
        "BMI_Report_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        +
        ".pdf"
    )


    pdf = canvas.Canvas(
        filename,
        pagesize=A4
    )


    page_width, page_height = A4


    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    pdf.setFillColor(
        colors.HexColor(
            "#0F172A"
        )
    )

    pdf.rect(
        0,
        page_height - 120,
        page_width,
        120,
        fill=1,
        stroke=0
    )


    pdf.setFillColor(
        colors.white
    )

    pdf.setFont(
        "Helvetica-Bold",
        30
    )

    pdf.drawString(
        50,
        page_height - 65,
        "BMI+"
    )


    pdf.setFont(
        "Helvetica",
        13
    )

    pdf.drawString(
        50,
        page_height - 88,
        "Smart BMI Health Report"
    )


    # -----------------------------------------------------
    # REPORT INFORMATION
    # -----------------------------------------------------

    y = page_height - 165


    pdf.setFillColor(
        colors.HexColor(
            "#0F172A"
        )
    )

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        50,
        y,
        "Latest BMI Result"
    )


    y -= 45


    pdf.setFont(
        "Helvetica",
        13
    )

    pdf.drawString(
        50,
        y,
        f"Date: {format_date(date_time)}"
    )


    y -= 30

    pdf.drawString(
        50,
        y,
        f"Weight: {weight:.1f} kg"
    )


    y -= 30

    pdf.drawString(
        50,
        y,
        f"Height: {height:.1f} cm"
    )


    y -= 45


    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawString(
        50,
        y,
        f"BMI: {bmi:.1f}"
    )


    y -= 35


    pdf.setFont(
        "Helvetica-Bold",
        17
    )

    pdf.drawString(
        50,
        y,
        f"Category: {category}"
    )


    y -= 55


    # -----------------------------------------------------
    # HEALTHY RANGE
    # -----------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        y,
        "Healthy Range"
    )


    y -= 30


    pdf.setFont(
        "Helvetica",
        13
    )

    pdf.drawString(
        50,
        y,
        "Healthy BMI: 18.5 – 24.9"
    )


    y -= 30


    pdf.drawString(
        50,
        y,
        (
            f"Healthy Weight: "
            f"{min_healthy_weight:.1f} – "
            f"{max_healthy_weight:.1f} kg"
        )
    )


    y -= 65


    # -----------------------------------------------------
    # BMI CATEGORIES
    # -----------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        y,
        "BMI Categories"
    )


    y -= 30


    pdf.setFont(
        "Helvetica",
        12
    )

    categories = [
        "Underweight: Below 18.5",
        "Normal: 18.5 – 24.9",
        "Overweight: 25 – 29.9",
        "Obesity: 30 and above"
    ]


    for item in categories:

        pdf.drawString(
            65,
            y,
            item
        )

        y -= 23


    y -= 25


    # -----------------------------------------------------
    # DISCLAIMER
    # -----------------------------------------------------

    pdf.setFont(
        "Helvetica-Oblique",
        10
    )

    pdf.setFillColor(
        colors.HexColor(
            "#64748B"
        )
    )

    pdf.drawString(
        50,
        y,
        "Note: BMI is a general screening measure and"
    )

    y -= 15

    pdf.drawString(
        50,
        y,
        "should not be considered a complete medical assessment."
    )


    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    pdf.setFillColor(
        colors.HexColor(
            "#0F172A"
        )
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        50,
        35,
        "Generated by BMI+ | Smart BMI Calculator"
    )


    pdf.save()


    messagebox.showinfo(
        "PDF Generated",
        f"Your BMI report has been created:\n\n{filename}"
    )


# =========================================================
# ABOUT WINDOW
# =========================================================

def open_about():

    about_window = ctk.CTkToplevel(
        app
    )

    about_window.title(
        "BMI+ | About"
    )

    about_window.geometry(
        "650x560"
    )

    about_window.configure(
        fg_color=BG_COLOR
    )


    logo = ctk.CTkLabel(
        about_window,
        text="BMI+",
        font=("Arial", 42, "bold"),
        text_color=ACCENT_COLOR
    )

    logo.pack(
        pady=(35, 5)
    )


    subtitle = ctk.CTkLabel(
        about_window,
        text="Smart BMI Calculator",
        font=("Arial", 18, "bold"),
        text_color=TEXT_COLOR
    )

    subtitle.pack(
        pady=(0, 25)
    )


    description = ctk.CTkLabel(
        about_window,
        text=(
            "BMI+ is a desktop BMI calculator designed to make\n"
            "BMI calculation simple, clear and easy to understand.\n\n"
            "The application supports multiple units, stores BMI\n"
            "history using SQLite and provides useful statistics\n"
            "and reports."
        ),
        font=("Arial", 14),
        text_color=SECONDARY_TEXT,
        justify="center"
    )

    description.pack(
        pady=10
    )


    features = ctk.CTkFrame(
        about_window,
        fg_color=CARD_COLOR,
        corner_radius=15
    )

    features.pack(
        fill="x",
        padx=40,
        pady=25
    )


    feature_text = ctk.CTkLabel(
        features,
        text=(
            "✓ BMI Calculation\n"
            "✓ Unit Conversion\n"
            "✓ SQLite History\n"
            "✓ BMI Statistics\n"
            "✓ Trend Chart\n"
            "✓ PDF Report"
        ),
        font=("Arial", 14),
        text_color=TEXT_COLOR,
        justify="left"
    )

    feature_text.pack(
        padx=30,
        pady=25
    )


    note = ctk.CTkLabel(
        about_window,
        text=(
            "BMI is a screening tool and should not replace\n"
            "professional medical advice."
        ),
        font=("Arial", 12),
        text_color=SECONDARY_TEXT,
        justify="center"
    )

    note.pack(
        pady=5
    )


# =========================================================
# HEADER
# =========================================================

header = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

header.pack(
    fill="x",
    padx=40,
    pady=(25, 5)
)


# =========================================================
# LOGO
# =========================================================

logo_frame = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

logo_frame.pack(
    side="left"
)


logo = ctk.CTkLabel(
    logo_frame,
    text="BMI+",
    font=("Arial", 29, "bold"),
    text_color=TEXT_COLOR
)

logo.pack(
    side="left"
)


tagline = ctk.CTkLabel(
    logo_frame,
    text="  Smart BMI Calculator",
    font=("Arial", 13),
    text_color=SECONDARY_TEXT
)

tagline.pack(
    side="left"
)


# =========================================================
# ABOUT BUTTON
# =========================================================

about_button = ctk.CTkButton(
    header,
    text="About",
    width=75,
    height=34,
    corner_radius=8,
    fg_color=CARD_COLOR,
    hover_color="#334155",
    command=open_about
)

about_button.pack(
    side="right"
)


# =========================================================
# INTRODUCTION
# =========================================================

intro = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

intro.pack(
    fill="x",
    padx=40,
    pady=(20, 15)
)


heading = ctk.CTkLabel(
    intro,
    text="Calculate your BMI",
    font=("Arial", 32, "bold"),
    text_color=TEXT_COLOR
)

heading.pack(
    anchor="w"
)


description = ctk.CTkLabel(
    intro,
    text=(
        "Enter your height and weight to understand "
        "your BMI and health range."
    ),
    font=("Arial", 14),
    text_color=SECONDARY_TEXT
)

description.pack(
    anchor="w",
    pady=(5, 0)
)


# =========================================================
# MAIN CONTENT
# =========================================================

content = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

content.pack(
    fill="both",
    expand=True,
    padx=40,
    pady=5
)


# =========================================================
# LEFT INPUT CARD
# =========================================================

input_card = ctk.CTkFrame(
    content,
    fg_color=CARD_COLOR,
    corner_radius=18
)

input_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)


# =========================================================
# INPUT TITLE
# =========================================================

input_title = ctk.CTkLabel(
    input_card,
    text="YOUR DETAILS",
    font=("Arial", 18, "bold"),
    text_color=TEXT_COLOR
)

input_title.pack(
    anchor="w",
    padx=30,
    pady=(25, 18)
)


# =========================================================
# WEIGHT
# =========================================================

weight_label = ctk.CTkLabel(
    input_card,
    text="Weight",
    font=("Arial", 13),
    text_color=SECONDARY_TEXT
)

weight_label.pack(
    anchor="w",
    padx=30
)


weight_frame = ctk.CTkFrame(
    input_card,
    fg_color="transparent"
)

weight_frame.pack(
    pady=(5, 12)
)


weight_entry = ctk.CTkEntry(
    weight_frame,
    placeholder_text="Enter weight",
    width=210,
    height=40
)

weight_entry.pack(
    side="left",
    padx=(0, 8)
)


weight_unit = ctk.CTkComboBox(
    weight_frame,
    values=["kg", "lb"],
    width=75,
    height=40
)

weight_unit.set(
    "kg"
)

weight_unit.pack(
    side="left"
)


# =========================================================
# HEIGHT
# =========================================================

height_label = ctk.CTkLabel(
    input_card,
    text="Height",
    font=("Arial", 13),
    text_color=SECONDARY_TEXT
)

height_label.pack(
    anchor="w",
    padx=30
)


height_frame = ctk.CTkFrame(
    input_card,
    fg_color="transparent"
)

height_frame.pack(
    pady=(5, 12)
)


height_entry = ctk.CTkEntry(
    height_frame,
    placeholder_text="Enter height",
    width=210,
    height=40
)

height_entry.pack(
    side="left",
    padx=(0, 8)
)


feet_entry = ctk.CTkEntry(
    height_frame,
    placeholder_text="ft",
    width=90,
    height=40
)


inches_entry = ctk.CTkEntry(
    height_frame,
    placeholder_text="in",
    width=90,
    height=40
)


height_unit = ctk.CTkComboBox(
    height_frame,
    values=["cm", "ft/in"],
    width=75,
    height=40,
    command=update_height_fields
)

height_unit.set(
    "cm"
)

height_unit.pack(
    side="left"
)


# =========================================================
# BUTTONS
# =========================================================

button_frame = ctk.CTkFrame(
    input_card,
    fg_color="transparent"
)

button_frame.pack(
    fill="x",
    padx=30,
    pady=(3, 10)
)


calculate_button = ctk.CTkButton(
    button_frame,
    text="Calculate BMI",
    height=45,
    corner_radius=10,
    font=("Arial", 14, "bold"),
    fg_color=ACCENT_COLOR,
    hover_color=ACCENT_HOVER,
    command=calculate_bmi
)

calculate_button.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 5)
)


reset_button = ctk.CTkButton(
    button_frame,
    text="Reset",
    height=45,
    width=90,
    corner_radius=10,
    font=("Arial", 14, "bold"),
    fg_color="#475569",
    hover_color="#64748B",
    command=reset_calculator
)

reset_button.pack(
    side="right"
)


# =========================================================
# HISTORY HEADER
# =========================================================

history_header = ctk.CTkFrame(
    input_card,
    fg_color="transparent"
)

history_header.pack(
    fill="x",
    padx=30,
    pady=(8, 0)
)


history_title = ctk.CTkLabel(
    history_header,
    text="BMI HISTORY",
    font=("Arial", 14, "bold"),
    text_color=TEXT_COLOR
)

history_title.pack(
    side="left"
)


# =========================================================
# HISTORY BUTTONS
# =========================================================

history_buttons = ctk.CTkFrame(
    history_header,
    fg_color="transparent"
)

history_buttons.pack(
    side="right"
)


delete_button = ctk.CTkButton(
    history_buttons,
    text="Delete Latest",
    width=95,
    height=28,
    corner_radius=7,
    font=("Arial", 10),
    fg_color="#475569",
    hover_color="#64748B",
    command=delete_latest_record
)

delete_button.pack(
    side="left",
    padx=2
)


clear_button = ctk.CTkButton(
    history_buttons,
    text="Clear All",
    width=75,
    height=28,
    corner_radius=7,
    font=("Arial", 10),
    fg_color="#7F1D1D",
    hover_color="#991B1B",
    command=clear_history
)

clear_button.pack(
    side="left",
    padx=2
)


# =========================================================
# SCROLLABLE HISTORY
# =========================================================

history_frame = ctk.CTkFrame(
    input_card,
    fg_color=CARD_DARK,
    corner_radius=12
)

history_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(8, 18)
)


history_text = ctk.CTkTextbox(
    history_frame,
    height=150,
    font=("Arial", 12),
    text_color=SECONDARY_TEXT,
    fg_color=CARD_DARK,
    border_width=0,
    corner_radius=8,
    wrap="word",
    activate_scrollbars=True
)

history_text.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=8
)

history_text.insert(
    "1.0",
    "No BMI records yet."
)

history_text.configure(
    state="disabled"
)


# =========================================================
# RIGHT RESULT CARD
# =========================================================

result_card = ctk.CTkFrame(
    content,
    fg_color=CARD_COLOR,
    corner_radius=18
)

result_card.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(10, 0)
)


# =========================================================
# RESULT TITLE
# =========================================================

result_title = ctk.CTkLabel(
    result_card,
    text="YOUR RESULT",
    font=("Arial", 18, "bold"),
    text_color=TEXT_COLOR
)

result_title.pack(
    anchor="w",
    padx=30,
    pady=(25, 15)
)


# =========================================================
# BMI VALUE
# =========================================================

bmi_value = ctk.CTkLabel(
    result_card,
    text="--",
    font=("Arial", 58, "bold"),
    text_color=TEXT_COLOR
)

bmi_value.pack(
    pady=(15, 2)
)


# =========================================================
# CATEGORY
# =========================================================

category = ctk.CTkLabel(
    result_card,
    text="Enter your details",
    font=("Arial", 21, "bold"),
    text_color=SECONDARY_TEXT
)

category.pack()


# =========================================================
# MESSAGE
# =========================================================

result_message = ctk.CTkLabel(
    result_card,
    text="Your BMI result will appear here.",
    font=("Arial", 13),
    text_color=SECONDARY_TEXT,
    justify="center"
)

result_message.pack(
    pady=15
)


# =========================================================
# BMI RANGE
# =========================================================

range_title = ctk.CTkLabel(
    result_card,
    text="BMI RANGE",
    font=("Arial", 14, "bold"),
    text_color=TEXT_COLOR
)

range_title.pack(
    pady=(5, 8)
)


bmi_progress = ctk.CTkProgressBar(
    result_card,
    width=350,
    height=18,
    corner_radius=10,
    progress_color=ACCENT_COLOR
)

bmi_progress.pack(
    padx=30,
    pady=(5, 8)
)

bmi_progress.set(
    0
)


range_labels = ctk.CTkLabel(
    result_card,
    text=(
        "Underweight     Normal     "
        "Overweight     Obesity"
    ),
    font=("Arial", 10),
    text_color=SECONDARY_TEXT
)

range_labels.pack(
    pady=(0, 8)
)


healthy_range = ctk.CTkLabel(
    result_card,
    text="Healthy BMI: 18.5 – 24.9",
    font=("Arial", 13),
    text_color=SECONDARY_TEXT
)

healthy_range.pack(
    pady=(5, 5)
)


healthy_weight = ctk.CTkLabel(
    result_card,
    text="Healthy Weight: --",
    font=("Arial", 14, "bold"),
    text_color=TEXT_COLOR
)

healthy_weight.pack(
    pady=(5, 10)
)


# =========================================================
# QUICK ACTION BUTTONS
# =========================================================

quick_actions = ctk.CTkFrame(
    result_card,
    fg_color="transparent"
)

quick_actions.pack(
    fill="x",
    padx=30,
    pady=(5, 10)
)


statistics_button = ctk.CTkButton(
    quick_actions,
    text="Statistics",
    height=38,
    corner_radius=9,
    fg_color="#334155",
    hover_color="#475569",
    command=open_statistics
)

statistics_button.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 4)
)


chart_button = ctk.CTkButton(
    quick_actions,
    text="BMI Trend",
    height=38,
    corner_radius=9,
    fg_color="#334155",
    hover_color="#475569",
    command=open_chart
)

chart_button.pack(
    side="left",
    fill="x",
    expand=True,
    padx=4
)


pdf_button = ctk.CTkButton(
    quick_actions,
    text="PDF Report",
    height=38,
    corner_radius=9,
    fg_color="#334155",
    hover_color="#475569",
    command=generate_pdf_report
)

pdf_button.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(4, 0)
)


# =========================================================
# STATISTICS VARIABLES
# =========================================================

latest_stat = ctk.CTkLabel(
    app,
    text="--"
)

average_stat = ctk.CTkLabel(
    app,
    text="--"
)

highest_stat = ctk.CTkLabel(
    app,
    text="--"
)

lowest_stat = ctk.CTkLabel(
    app,
    text="--"
)

total_stat = ctk.CTkLabel(
    app,
    text="0"
)


# =========================================================
# BOTTOM BMI CATEGORIES
# =========================================================

categories = ctk.CTkFrame(
    app,
    fg_color=CARD_COLOR,
    corner_radius=15
)

categories.pack(
    fill="x",
    padx=40,
    pady=(8, 20)
)


categories_title = ctk.CTkLabel(
    categories,
    text="BMI CATEGORIES",
    font=("Arial", 14, "bold"),
    text_color=TEXT_COLOR
)

categories_title.pack(
    pady=(12, 5)
)


categories_text = ctk.CTkLabel(
    categories,
    text=(
        "Underweight  < 18.5    •    "
        "Normal  18.5 – 24.9    •    "
        "Overweight  25 – 29.9    •    "
        "Obesity  30+"
    ),
    font=("Arial", 12),
    text_color=SECONDARY_TEXT
)

categories_text.pack(
    pady=(0, 13)
)


# =========================================================
# LOAD EXISTING HISTORY
# =========================================================

load_history()

update_statistics()


# =========================================================
# START APPLICATION
# =========================================================

app.mainloop()