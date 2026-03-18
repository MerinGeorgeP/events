# 🎓 EventHub

A unified university platform that connects students and organisers to
discover, manage, and participate in events seamlessly.

------------------------------------------------------------------------

## 🚀 Overview

EventHub is a Streamlit-based web application designed to: - Help
students discover relevant events - Enable organisers to create and
manage events - Provide filtering, search, and personalised
recommendations - Manage certificates and participation records

------------------------------------------------------------------------

## ✨ Features

### 👤 Participants

-   Register & login
-   Discover events with smart filters
-   Search events by name
-   View detailed event pages
-   Access personalised suggestions

### 🎯 Organisers

-   Create and manage events
-   Upload event posters
-   Add event details (date, venue, topics, etc.)
-   View and manage created events

### 🔍 Smart Filtering

-   Filter by:
    -   Topics (AI/ML, Web Dev, etc.)
    -   Level (Beginner → Advanced)
    -   Fees (Free/Paid)
    -   Activity points

------------------------------------------------------------------------

## 🏗 Architecture

### 🔹 Frontend

-   Built using **Streamlit**
-   Interactive dashboards for:
    -   Participants
    -   Organisers

### 🔹 Backend

-   Uses **SQLite**
-   Handles:
    -   User authentication
    -   Event storage
    -   Certificate tracking

------------------------------------------------------------------------

## 🗄 Database Schema

### Users Table

-   username (Primary Key)
-   password
-   role (participant / organiser)
-   name
-   college
-   interests

### Events Table

-   id
-   organiser
-   name
-   date
-   time
-   venue
-   poster
-   description
-   fees
-   reg_link
-   level
-   topics
-   activity_points

### Certificates Table

-   event_id
-   participant
-   file

------------------------------------------------------------------------

## ⚙️ Workflow

### 1. Authentication

-   Users register as participant or organiser
-   Login with credentials
-   Session state maintains user login

### 2. Organiser Flow

-   Create events
-   Upload posters
-   Manage events

### 3. Participant Flow

-   Browse events
-   Apply filters
-   View event details
-   Register via external link

### 4. Event Interaction

-   Detailed event page includes:
    -   Organiser profile
    -   Event description
    -   Registration link

------------------------------------------------------------------------

## 🛠 Tech Stack

-   **Frontend:** Streamlit\
-   **Backend:** Python\
-   **Database:** SQLite\
-   **Storage:** Local file system (posters, certificates, profile pics)

------------------------------------------------------------------------

## 📂 Project Structure

    eventhub.py          # Main application file
    eventhub.db          # SQLite database
    uploads/
        posters/         # Event posters
        certificates/    # Certificates
        profile_pics/    # Organiser profile images

------------------------------------------------------------------------

## ▶️ How to Run

``` bash
# Install dependencies
pip install streamlit

# Run the app
streamlit run eventhub.py
```

------------------------------------------------------------------------

## 🔐 Security Notes

-   Basic authentication using username & password
-   Session-based login handling
-   (Future improvement: password hashing & JWT)

------------------------------------------------------------------------

## 🚀 Future Improvements

-   Password hashing for security
-   Email notifications
-   Certificate auto-generation
-   Recommendation system (AI-based)
-   Cloud deployment

------------------------------------------------------------------------

## 🙌 Acknowledgment

This project demonstrates a full-stack event management system with
role-based dashboards and real-time filtering.

------------------------------------------------------------------------

## 📎 Source

Based on implementation in eventhub.py
