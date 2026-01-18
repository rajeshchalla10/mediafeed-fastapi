# 📸 Mediafeed – FastAPI Social Media Backend

Mediafeed is a lightweight **Instagram‑style REST API** built with **FastAPI**, designed to demonstrate the core features of a social media backend. It provides a clean, modular foundation for building feed‑based applications where users can share posts, interact, and engage with content.

---

## 🚀 Features
- 👤 **User Accounts**: registration, login, JWT authentication
- 🖼️ **Posts & Feeds**: create posts with captions, fetch personalized feeds
- 💬 **Interactions**: likes, comments, and social engagement endpoints
- 🔒 **Secure Authentication**: password hashing & token management
- 📑 **Interactive API Docs**: auto‑generated with Swagger UI & ReDoc
- 🗄️ **Database Integration**: SQLAlchemy/SQLModel for persistence

---

## 📂 Project Structure


```
mediafeed/
│── app/
│   ├── app.py          
│   ├── users.py        
│   ├── images.py 
│   ├── schemas.py       # Pydantic schemas
│   └── db.py 
│── main.py              # Entry point
│── frontend.py
│── requirements.txt
│── README.md

```



## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License.
