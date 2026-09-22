import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="BMI+ | Smart BMI Calculator",
    page_icon="⚖️",
    layout="wide"
)

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


def get_all_records():
    connection = sqlite3.connect(DATABASE_NAME)

    records = pd.read_sql_query(
        """
        SELECT id, date_time, weight, height, bmi, category
        FROM bmi_records
        ORDER BY id DESC
        """,
        connection
    )

    connection.close()

    return records


def save_record(weight, height, bmi, category):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bmi_records
        (date_time, weight, height, bmi, category)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        weight,
        height,
        bmi,
        category
    ))

    connection.commit()
    connection.close()


def delete_latest():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM bmi_records
        WHERE id = (
            SELECT MAX(id)
            FROM bmi_records
        )
    """)

    connection.commit()
    connection.close()


def clear_history():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("DELETE FROM bmi_records")

    connection.commit()
    connection.close()


# =========================================================
# BMI FUNCTIONS
# =========================================================

def get_category(bmi):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obesity"


def category_color(category):

    if category == "Underweight":
        return "#3B82F6"

    elif category == "Normal":
        return "#22C55E"

    elif category == "Overweight":
        return "#F59E0B"

    return "#EF4444"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0F172A;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.title {
    font-size: 42px;
    font-weight: 800;
}

.subtitle {
    color: #94A3B8;
    font-size: 17px;
}

.result-box {
    background-color: #1E293B;
    padding: 30px;
    border-radius: 18px;
    text-align: center;
}

.bmi-number {
    font-size: 60px;
    font-weight: 800;
}

.category {
    font-size: 24px;
    font-weight: 700;
}

.info-box {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">BMI+</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Smart BMI Calculator</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# INPUT SECTION
# =========================================================

left, right = st.columns(2)


with left:

    st.subheader("Your Details")

    weight_unit = st.selectbox(
        "Weight Unit",
        ["kg", "lb"]
    )

    weight = st.number_input(
        "Weight",
        min_value=0.0,
        max_value=700.0,
        value=60.0,
        step=0.1
    )


with right:

    height_unit = st.selectbox(
        "Height Unit",
        ["cm", "ft/in"]
    )

    if height_unit == "cm":

        height_cm = st.number_input(
            "Height (cm)",
            min_value=0.0,
            max_value=300.0,
            value=170.0,
            step=0.1
        )

    else:

        feet, inches = st.columns(2)

        with feet:

            height_feet = st.number_input(
                "Feet",
                min_value=0,
                max_value=8,
                value=5
            )

        with inches:

            height_inches = st.number_input(
                "Inches",
                min_value=0.0,
                max_value=11.99,
                value=7.0,
                step=0.1
            )


st.write("")


calculate = st.button(
    "Calculate BMI",
    type="primary",
    use_container_width=True
)


# =========================================================
# CALCULATE BMI
# =========================================================

if calculate:

    # -----------------------------------------------------
    # WEIGHT CONVERSION
    # -----------------------------------------------------

    weight_kg = weight

    if weight_unit == "lb":
        weight_kg = weight * 0.453592


    # -----------------------------------------------------
    # HEIGHT CONVERSION
    # -----------------------------------------------------

    if height_unit == "cm":

        height_value_cm = height_cm

    else:

        height_value_cm = (
            height_feet * 30.48
            +
            height_inches * 2.54
        )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if weight_kg <= 0:

        st.error("Weight must be greater than zero.")

    elif weight_kg < 20 or weight_kg > 300:

        st.error(
            "Please enter a weight between 20 kg and 300 kg."
        )

    elif height_value_cm <= 0:

        st.error("Height must be greater than zero.")

    elif height_value_cm < 80 or height_value_cm > 250:

        st.error(
            "Please enter a height between 80 cm and 250 cm."
        )

    else:

        # -------------------------------------------------
        # BMI
        # -------------------------------------------------

        height_m = height_value_cm / 100

        bmi = weight_kg / (height_m ** 2)

        category = get_category(bmi)


        # -------------------------------------------------
        # HEALTHY WEIGHT
        # -------------------------------------------------

        min_weight = 18.5 * (height_m ** 2)

        max_weight = 24.9 * (height_m ** 2)


        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        save_record(
            weight_kg,
            height_value_cm,
            bmi,
            category
        )


        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        st.divider()

        st.subheader("Your Result")

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "BMI",
                f"{bmi:.1f}"
            )


        with col2:

            st.metric(
                "Category",
                category
            )


        with col3:

            st.metric(
                "Healthy BMI",
                "18.5 – 24.9"
            )


        st.markdown(
            f"""
            <div class="result-box">

            <div class="bmi-number">
            {bmi:.1f}
            </div>

            <div class="category"
                 style="color:{category_color(category)}">

            {category}

            </div>

            <br>

            Healthy Weight:
            <b>{min_weight:.1f} – {max_weight:.1f} kg</b>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.success(
            f"Your BMI is {bmi:.1f}. "
            f"Your BMI category is {category}."
        )


# =========================================================
# HISTORY
# =========================================================

st.divider()

st.subheader("BMI History")

records = get_all_records()


if records.empty:

    st.info(
        "No BMI records yet. "
        "Calculate your BMI to create history."
    )

else:

    display_records = records.copy()

    display_records["date_time"] = pd.to_datetime(
        display_records["date_time"]
    ).dt.strftime(
        "%d %b %Y, %I:%M %p"
    )

    display_records["weight"] = display_records[
        "weight"
    ].round(1)

    display_records["height"] = display_records[
        "height"
    ].round(1)

    display_records["bmi"] = display_records[
        "bmi"
    ].round(1)


    st.dataframe(
        display_records[
            [
                "date_time",
                "weight",
                "height",
                "bmi",
                "category"
            ]
        ].rename(
            columns={
                "date_time": "Date",
                "weight": "Weight (kg)",
                "height": "Height (cm)",
                "bmi": "BMI",
                "category": "Category"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


    history_col1, history_col2 = st.columns(2)


    with history_col1:

        if st.button(
            "Delete Latest Record",
            use_container_width=True
        ):

            delete_latest()

            st.success(
                "Latest record deleted."
            )

            st.rerun()


    with history_col2:

        if st.button(
            "Clear All History",
            use_container_width=True
        ):

            clear_history()

            st.success(
                "All BMI history deleted."
            )

            st.rerun()


# =========================================================
# STATISTICS
# =========================================================

st.divider()

st.subheader("BMI Statistics")

records = get_all_records()


if records.empty:

    st.info(
        "Statistics will appear after you calculate BMI."
    )

else:

    bmi_values = records["bmi"]

    stat1, stat2, stat3, stat4 = st.columns(4)


    with stat1:

        st.metric(
            "Latest BMI",
            f"{bmi_values.iloc[0]:.1f}"
        )


    with stat2:

        st.metric(
            "Average BMI",
            f"{bmi_values.mean():.1f}"
        )


    with stat3:

        st.metric(
            "Highest BMI",
            f"{bmi_values.max():.1f}"
        )


    with stat4:

        st.metric(
            "Total Records",
            len(records)
        )


# =========================================================
# BMI TREND
# =========================================================

st.divider()

st.subheader("BMI Trend")


records = get_all_records()


if len(records) < 2:

    st.info(
        "Calculate at least 2 BMI records "
        "to see your BMI trend."
    )

else:

    chart_data = records[
        ["date_time", "bmi"]
    ].copy()

    chart_data["date_time"] = pd.to_datetime(
        chart_data["date_time"]
    )

    chart_data = chart_data.sort_values(
        "date_time"
    )

    chart_data = chart_data.set_index(
        "date_time"
    )

    st.line_chart(
        chart_data["bmi"]
    )


# =========================================================
# BMI CATEGORIES
# =========================================================

st.divider()

st.subheader("BMI Categories")

category_col1, category_col2, category_col3, category_col4 = st.columns(4)


with category_col1:

    st.markdown(
        """
        **Underweight**

        BMI below **18.5**
        """
    )


with category_col2:

    st.markdown(
        """
        **Normal**

        BMI **18.5 – 24.9**
        """
    )


with category_col3:

    st.markdown(
        """
        **Overweight**

        BMI **25 – 29.9**
        """
    )


with category_col4:

    st.markdown(
        """
        **Obesity**

        BMI **30 and above**
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "BMI+ | Smart BMI Calculator"
)

st.caption(
    "BMI is a general screening measure and "
    "should not replace professional medical advice."
)