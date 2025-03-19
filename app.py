import streamlit as st
import json
import os
import pandas as pd

# File to save/load the library
LIBRARY_FILE = "library.txt"

# Initialize session state to store the library
if 'library' not in st.session_state:
    st.session_state.library = []
    # Load library from file at startup
    try:
        if os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, 'r') as file:
                st.session_state.library = json.load(file)
            st.success(f"Library loaded from {LIBRARY_FILE}")
    except Exception as e:
        st.error(f"Error loading library: {e}")
        st.session_state.library = []

# Function to save the library to file
def save_library():
    try:
        with open(LIBRARY_FILE, 'w') as file:
            json.dump(st.session_state.library, file, indent=4)
        st.success(f"Library saved to {LIBRARY_FILE}")
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Function to add a book
def add_book():
    st.header("Add a Book")
    
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=1000, max_value=2100, value=2023)
        genre = st.text_input("Genre")
        read_status = st.selectbox("Have you read this book?", ["No", "Yes"])
        
        submitted = st.form_submit_button("Add Book")
        
        if submitted and title and author:
            book = {
                "title": title,
                "author": author,
                "year": int(year),
                "genre": genre,
                "read": read_status == "Yes"
            }
            
            st.session_state.library.append(book)
            save_library()
            st.success(f"'{title}' by {author} added successfully!")
        elif submitted:
            st.warning("Title and author are required!")

# Function to remove a book
def remove_book():
    st.header("Remove a Book")
    
    if not st.session_state.library:
        st.info("Your library is empty.")
        return
    
    # Create a dataframe for display
    df = pd.DataFrame(st.session_state.library)
    
    # Add a column with delete buttons
    book_to_remove = st.selectbox(
        "Select a book to remove:",
        options=range(len(st.session_state.library)),
        format_func=lambda x: f"{st.session_state.library[x]['title']} by {st.session_state.library[x]['author']}"
    )
    
    if st.button("Remove Selected Book"):
        removed_book = st.session_state.library.pop(book_to_remove)
        save_library()
        st.success(f"'{removed_book['title']}' removed successfully!")

# Function to search for a book
def search_book():
    st.header("Search for Books")
    
    if not st.session_state.library:
        st.info("Your library is empty.")
        return
    
    search_by = st.radio("Search by:", ["Title", "Author"])
    search_term = st.text_input("Enter search term:")
    
    if search_term:
        matching_books = []
        search_term = search_term.lower()
        
        for book in st.session_state.library:
            if (search_by == "Title" and search_term in book["title"].lower()) or \
               (search_by == "Author" and search_term in book["author"].lower()):
                matching_books.append(book)
        
        if matching_books:
            st.subheader("Matching Books:")
            display_books(matching_books)
        else:
            st.info("No matching books found.")

# Function to display books
def display_books(books_to_display=None):
    books_list = books_to_display if books_to_display is not None else st.session_state.library
    
    if not books_list:
        st.info("No books to display.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(books_list)
    
    # Rename columns for display
    if not df.empty:
        # Make sure all expected columns exist
        for col in ["title", "author", "year", "genre", "read"]:
            if col not in df.columns:
                df[col] = ""
                
        # Rename and reorder columns
        df = df[["title", "author", "year", "genre", "read"]]
        df.columns = ["Title", "Author", "Year", "Genre", "Read"]
        
        # Convert boolean to Yes/No
        df["Read"] = df["Read"].map({True: "Yes", False: "No"})
        
        # Display the table
        st.dataframe(df)

# Function to display statistics
def display_stats():
    st.header("Library Statistics")
    
    if not st.session_state.library:
        st.info("Your library is empty.")
        return
    
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read"])
    percentage_read = (read_books / total_books) * 100 if total_books > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Books", total_books)
    
    with col2:
        st.metric("Books Read", read_books)
    
    with col3:
        st.metric("Percentage Read", f"{percentage_read:.1f}%")
    
    # Genre distribution
    if total_books > 0:
        st.subheader("Genre Distribution")
        genre_counts = {}
        for book in st.session_state.library:
            genre = book["genre"]
            if genre in genre_counts:
                genre_counts[genre] += 1
            else:
                genre_counts[genre] = 1
        
        genre_df = pd.DataFrame({
            "Genre": list(genre_counts.keys()),
            "Count": list(genre_counts.values())
        })
        
        st.bar_chart(genre_df.set_index("Genre"))

# Main function
def main():
    st.set_page_config(
        page_title="Personal Library Manager By Raza",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Personal Library Manager By Raza")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["View All Books", "Add a Book", "Remove a Book", "Search for Books", "Statistics"]
    )
    
    # Display the selected page
    if page == "View All Books":
        st.header("Your Library")
        display_books()
        
        if st.button("Save Library"):
            save_library()
    
    elif page == "Add a Book":
        add_book()
    
    elif page == "Remove a Book":
        remove_book()
    
    elif page == "Search for Books":
        search_book()
    
    elif page == "Statistics":
        display_stats()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("Personal Library Manager v1.0")

if __name__ == "__main__":
    main()

