# Live Coding Challenge: Book Catalog API
 
## Scenario:
Build a minimal but robust RESTful API for a book catalog, focusing on best practices in API design, type safety, data validation, and Pythonic coding. You may choose any modern Python framework and supporting libraries you feel are most appropriate.
 
## Requirements:
 
### 1. API Endpoints:
   - `POST /books/`:  
     Accept a JSON body with:
     - `title` (string, required)
     - `author` (string, required)
     - `year` (integer, required, 1400 ≤ year ≤ current year)
     - `tags` (optional list of strings)
     Return the created book with a generated unique integer ID.
   - `GET /books/`:  
     Return a paginated list of all books, with optional filters by `author`, `year`, or a full-text search on `title`.
   - `GET /books/{id}`:  
     Return a single book by its unique ID.
   - (Optional, if time allows) `DELETE /books/{id}`:  
     Remove a book from the catalog.
 
### 2. Logic & Type Safety:
   - Use Python type hints consistently.
   - Use appropriate data validation to ensure input correctness (e.g., validate `year` range, required fields, etc.).
   - Return meaningful status codes and error messages.
 
### 3. Storage:
   - Use an in-memory store (such as a dict or list); no database is needed.
 
### 4. Your Choices:  
   - You may choose any frameworks and libraries you feel are best for the task, as well as any validation or serialization libraries you prefer.
   - Be prepared to briefly explain your choices.
 
### 5. **Bonus (for differentiation):**
   - Add sorting by year or author.
   - Implement a `/stats` endpoint that returns the total number of books and the count of unique authors.
 
## **Instructions for Candidate:**
- You have 60 minutes.
- Narrate your decisions and approach as you code.
- Your API should be runnable as a standalone script.
- Focus on code quality, robustness, and maintainability.
