import streamlit as st
import sqlite3
from datetime import date

conn = sqlite3.connect(
    "gym.db",
    check_same_thread=False
)

c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    exercise TEXT,
    weight REAL,
    reps INTEGER,
    notes TEXT,
    workout_date TEXT
)
""")

st.title("Gym Tracker")

username = st.text_input(
    "Enter Username"
)

if username:

    st.success(
        f"Welcome {username}"
    )

    st.subheader("Add Workout")

    exercise = st.text_input(
        "Exercise"
    )

    weight = st.number_input(
        "Weight",
        min_value=0.0
    )

    reps = st.number_input(
        "Reps",
        min_value=1,
        step=1
    )

    notes = st.text_input(
        "Notes"
    )

    workout_date = st.date_input(
        "Date",
        date.today()
    )

    if st.button("Save Workout"):

        c.execute(
            """
            INSERT INTO workouts (
                username,
                exercise,
                weight,
                reps,
                notes,
                workout_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                exercise,
                weight,
                reps,
                notes,
                str(workout_date)
            )
        )

        conn.commit()

        st.success(
            "Workout Saved!"
        )

    search = st.text_input(
        "Search Exercise"
    )

    st.subheader("Workout History")

    if search:

        workouts = c.execute(
            """
            SELECT
                id,
                exercise,
                weight,
                reps,
                notes,
                workout_date
            FROM workouts
            WHERE username=?
            AND exercise LIKE ?
            ORDER BY workout_date DESC
            """,
            (
                username,
                f"%{search}%"
            )
        ).fetchall()

    else:

        workouts = c.execute(
            """
            SELECT
                id,
                exercise,
                weight,
                reps,
                notes,
                workout_date
            FROM workouts
            WHERE username=?
            ORDER BY workout_date DESC
            """,
            (username,)
        ).fetchall()

    for workout in workouts:

        workout_id = workout[0]
        exercise_name = workout[1]
        weight_amount = workout[2]
        reps_amount = workout[3]
        notes_text = workout[4]

        formatted_date = (
            date.fromisoformat(workout[5])
            .strftime("%B %d, %Y")
        )

        col1, col2 = st.columns([4,1])

        with col1:

            st.write(
                f"{exercise_name} - "
                f"{weight_amount} lbs x "
                f"{reps_amount} reps - "
                f"{formatted_date}"
            )

            if notes_text:

                st.caption(
                    f"Notes: {notes_text}"
                )

        with col2:

            if st.button(
                "Delete",
                key=workout_id
            ):

                c.execute(
                    """
                    DELETE FROM workouts
                    WHERE id=?
                    """,
                    (workout_id,)
                )

                conn.commit()

                st.rerun()

    if st.button("Show Progression"):

        exercises = c.execute(
            """
            SELECT DISTINCT exercise
            FROM workouts
            WHERE username=?
            """,
            (username,)
        ).fetchall()

        for ex in exercises:

            exercise_name = ex[0]

            records = c.execute(
                """
                SELECT
                    weight,
                    reps,
                    workout_date
                FROM workouts
                WHERE username=?
                AND exercise=?
                ORDER BY workout_date
                """,
                (
                    username,
                    exercise_name
                )
            ).fetchall()

            if len(records) > 1:

                improvements = []

                previous_weight = records[0][0]

                for record in records[1:]:

                    current_weight = record[0]
                    current_reps = record[1]
                    current_date = record[2]

                    difference = (
                        current_weight
                        - previous_weight
                    )

                    if difference > 0:

                        formatted_date = (
                            date.fromisoformat(
                                current_date
                            ).strftime(
                                "%B %d, %Y"
                            )
                        )

                        improvements.append(
                            f"{formatted_date}: "
                            f"+{difference} lbs "
                            f"({previous_weight} "
                            f"→ {current_weight}) "
                            f"x {current_reps} reps"
                        )

                    previous_weight = current_weight

                if len(improvements) > 0:

                    st.markdown(
                        f"## {exercise_name}"
                    )

                    for improvement in improvements:

                        st.write(improvement)

    st.subheader("Personal Records")

    prs = c.execute(
        """
        SELECT
            exercise,
            MAX(weight)
        FROM workouts
        WHERE username=?
        GROUP BY exercise
        """,
        (username,)
    ).fetchall()

    for pr in prs:

        st.write(
            f"{pr[0]} PR: "
            f"{pr[1]} lbs"
        )
